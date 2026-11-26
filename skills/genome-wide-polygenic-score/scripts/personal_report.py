"""Compute the published raw GPS sum, with complete-variant coverage only.

Python standard library. A temporary SQLite index keeps genotype memory bounded.
No genotype is sent over the network; only a fixed public weight URL is fetched.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import sqlite3
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import presets
import skillkit
from paper_card import lines as paper_card_lines

AUTOSOMES = frozenset(str(i) for i in range(1, 23))


class InputError(Exception):
    def __init__(self, problem):
        self.problem = problem
        super().__init__(problem.message_zh)


class ResourceError(Exception):
    pass


def fail(key, message, kind="input"):
    raise InputError(skillkit.Problem(key, key, kind, message))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def obtain_weights(disease, cache, offline=False):
    """Fetch the exact author release into a cache; never use a changed file."""
    model = presets.MODELS[disease]
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / (disease + ".zip")
    if dest.exists():
        if digest(dest) != model["zip_sha256"]:
            raise ResourceError(f"权重缓存 {dest} 的 SHA-256 不符，请移走该损坏文件后重试。")
        return dest
    if offline:
        raise ResourceError(f"离线缓存缺少 {dest.name}；需要先由技能取得公开权重。")
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=cache, suffix=".download", delete=False) as f:
            temp = Path(f.name)
            with urllib.request.urlopen(model["url"], timeout=60) as response:
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    f.write(block)
        if digest(temp) != model["zip_sha256"]:
            raise ResourceError("下载的公开权重与已核读的 v3 文件校验和不符，未计算。")
        os.replace(temp, dest)
        return dest
    except (OSError, urllib.error.URLError) as e:
        raise ResourceError(f"公开权重下载失败：{e}。请重试；不需要用户提供权重。") from e
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def variant_key(raw):
    """Match exact hg19 locus and unordered allele pair; never strand-flip."""
    parts = raw.split(":")
    if len(parts) != 4:
        fail("variant", f"变异 {raw!r} 必须写为 chromosome:position:allele1:allele2。")
    chrom, pos, a, b = parts
    if chrom.startswith("chr"):
        chrom = chrom[3:]
    if chrom not in AUTOSOMES or not pos.isdigit() or int(pos) < 1:
        fail("variant", f"变异 {raw!r} 不是有效的常染色体位置。")
    if not re.fullmatch("[ACGT]+", a) or not re.fullmatch("[ACGT]+", b) or a == b:
        fail("variant", f"变异 {raw!r} 需要两个不同的正链 DNA 等位基因。")
    left, right = sorted((a, b))
    return f"{chrom}:{int(pos)}:{left}:{right}", (a, b)


def load_genotypes(path, conn, manifest):
    spec = skillkit.spec_by_key(manifest, "dosage_copies")
    aliases = skillkit.alias_index([spec])
    opener = gzip.open if str(path).endswith(".gz") else open
    count = 0
    try:
        with opener(path, "rt", encoding="utf-8-sig", newline="") as f:
            first = f.readline()
            f.seek(0)
            reader = csv.DictReader(f, delimiter="\t" if "\t" in first else ",")
            fields = reader.fieldnames or []
            dose_columns = [x for x in fields if skillkit.fold_name(x) in aliases]
            if len(fields) != len(set(fields)) or len(dose_columns) != 1 or not {
                    "variant", "dosage_allele", "unit"}.issubset(fields):
                fail("genotypes", "表头需要 variant,dosage_allele,dosage_copies,unit；剂量列也可写 DS 或等位基因剂量。", "header")
            dose_col = dose_columns[0]
            for number, row in enumerate(reader, 2):
                if None in row or any(v is None for v in row.values()):
                    fail("genotypes", f"第 {number} 行的列数与表头不符。", "header")
                key, alleles = variant_key(row["variant"].strip())
                allele = row["dosage_allele"].strip()
                if allele not in alleles:
                    fail("dosage_allele", f"第 {number} 行计数的等位基因不在该变异的等位基因对内。")
                unit = row["unit"].strip()
                if not unit:
                    fail("dosage_copies", f"第 {number} 行必须写单位 1（拷贝计数）。", "unit_missing")
                factor = skillkit.unit_factor(spec, unit)
                if factor is None:
                    fail("dosage_copies", f"第 {number} 行剂量单位 {unit!r} 不接受；需要单位 1（拷贝计数）。", "unit")
                try:
                    value = skillkit.parse_number(row[dose_col]) * factor
                except ValueError:
                    fail("dosage_copies", f"第 {number} 行剂量缺失或不是有限数值；需要 0–2 拷贝。", "parse")
                problem = skillkit.range_problem(spec, value, f"第 {number} 行，单位 {unit}")
                if problem:
                    raise InputError(problem)
                try:
                    conn.execute("INSERT INTO genotypes VALUES (?, ?, ?)", (key, allele, value))
                except sqlite3.IntegrityError:
                    fail("variant", f"第 {number} 行重复出现同一变异 {key}；每个位点只能有一行。", "duplicate")
                count += 1
                if count % 100000 == 0:
                    conn.commit()
    except (OSError, UnicodeError, csv.Error, EOFError) as e:
        fail("genotypes", f"无法读取个人剂量表：{e}。需要单样本 CSV/TSV，可 gzip。", "file")
    if not count:
        fail("genotypes", "个人剂量表没有数据行。", "missing")
    conn.commit()
    return count


def contribution(dosage, dosage_allele, effect_allele, weight):
    return (dosage if dosage_allele == effect_allele else 2.0 - dosage) * weight


def score(conn, archive, model):
    n = matched = missing = 0
    examples = []
    cursor = conn.cursor()

    def products():
        nonlocal n, matched, missing
        with zipfile.ZipFile(archive) as z:
            if z.namelist() != [model["member"]]:
                raise ResourceError("权重压缩包成员名称不符合已核读的发布版本。")
            with z.open(model["member"]) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8")
                rows = csv.DictReader((line for line in text if not line.startswith("#")), delimiter="\t")
                expected = ["variant", "effect_allele", "effect_weight", "chr", "position_hg19", "A1", "A2"]
                if rows.fieldnames != expected:
                    raise ResourceError("公开权重表头不符合已核读版本。")
                for row in rows:
                    key, alleles = variant_key(row["variant"])
                    effect = row["effect_allele"]
                    weight = float(row["effect_weight"])
                    if effect not in alleles or not math.isfinite(weight):
                        raise ResourceError("公开权重中出现无效等位基因或非有限数值。")
                    n += 1
                    hit = cursor.execute("SELECT allele, dosage FROM genotypes WHERE variant=?", (key,)).fetchone()
                    if hit is None:
                        missing += 1
                        if len(examples) < 20:
                            examples.append(row["variant"])
                        continue
                    matched += 1
                    yield contribution(hit[1], hit[0], effect, weight)

    total = math.fsum(products())
    if n != model["count"]:
        raise ResourceError(f"公开权重有 {n} 行，与应有 {model['count']} 行不符。")
    if missing:
        fail("genotypes", f"所选模型需要 {n} 个位点，已匹配 {matched} 个，缺少 {missing} 个。"
             f"未计算分数，不以零或均值补齐。前 {len(examples)} 个缺项：{', '.join(examples)}。"
             "请取得对应 hg19 正链位点的基因型或填补剂量；普通消费级芯片原始表通常不完整。", "missing")
    return total, matched


def write_failure(out, manifest, problems, code=3):
    path = skillkit.write_problems(out, problems, presets.TITLE, presets.BOUNDARY)
    body = path.read_text(encoding="utf-8").split("\n", 1)[1]
    path.write_text("\n".join([f"# {presets.TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
    skillkit.write_result(out, manifest, {spec["key"]: None for spec in manifest["outputs"]})
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=presets.TITLE)
    parser.add_argument("--genotypes", type=Path)
    parser.add_argument("--disease")
    parser.add_argument("--build")
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--cache", type=Path, default=Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "longevity-skills/genome-wide-polygenic-score")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "result.json", "problems.json", "provenance.json"):
        (out / name).unlink(missing_ok=True)
    try:
        if args.disease not in presets.MODELS:
            fail("disease", "请选择要计算的疾病：cad、af、t2d、ibd 或 bc。", "missing")
        if args.build not in ("hg19", "GRCh37"):
            fail("build", "需要明确的 hg19/GRCh37 坐标；不接受 hg38，也不自动转换。")
        if args.sex is not None and args.sex not in ("female", "male"):
            fail("sex", "性别参数只接受 female 或 male。")
        if args.disease == "bc" and args.sex != "female":
            fail("sex", "本论文乳腺癌分析限女性；bc 需要 --sex female。")
        age = None
        if args.age is not None:
            try:
                age = skillkit.parse_number(args.age)
            except ValueError:
                fail("age", "年龄必须是有限数值，单位为岁。")
            problems = skillkit.check_scalar(manifest, "age", age)
            if problems:
                raise InputError(problems[0])
        if args.genotypes is None:
            fail("genotypes", "缺少个人单样本基因型剂量表，请提供 --genotypes。", "missing")
        # Check personal data before initiating any public download.
        with tempfile.TemporaryDirectory(prefix="gps-private-", dir=out) as temp:
            conn = sqlite3.connect(str(Path(temp) / "genotypes.sqlite"))
            try:
                conn.execute("PRAGMA journal_mode=OFF")
                conn.execute("PRAGMA cache_size=-32768")
                conn.execute("CREATE TABLE genotypes (variant TEXT PRIMARY KEY, allele TEXT, dosage REAL) WITHOUT ROWID")
                count = load_genotypes(args.genotypes, conn, manifest)
                model = presets.MODELS[args.disease]
                if count < model["count"]:
                    fail("genotypes", f"输入仅 {count} 个唯一位点，所选模型需要 {model['count']} 个位点；请补齐，未计算。", "missing")
                archive = obtain_weights(args.disease, args.cache, offline=args.offline)
                total, matched = score(conn, archive, model)
            finally:
                conn.close()
        output = {"disease": args.disease, "raw_score": total,
                  "variants_scored": matched, "extra_variants": count - matched}
        skillkit.write_result(out, manifest, output)
        lines = [f"# {presets.TITLE}", "", *paper_card_lines(), "", "## 你的原始分数", "",
                 f"疾病：{model['label_zh']}。原始加权分数：**{total:.12g}**。",
                 f"纳入 {matched:,} 个已发布位点；输入中另外 {count - matched:,} 个位点未用于该模型。", "",
                 "该数未经个人示例复现。它是逐位点拷贝计数与权重的乘积之和，没有转换为概率。",
                 "未计算标准分或风险百分位：缺少可移植的参照分布、个人概率模型截距及相应校准参数。",
                 "研究主要来自白人英国祖源人群；对中国人及其他祖源的个人风险解释未由本文验证。",
                 "需要经过质量控制的正链基因型或填补剂量；本程序不执行基因型填补、坐标转换或质量评估。"]
        if age is not None and not 40 <= age <= 69:
            lines += ["你的年龄在本研究招募年龄 40–69 岁之外；原始求和不使用年龄，适用性尚未验证。"]
        lines += ["", f"边界: {presets.BOUNDARY}"]
        (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (out / "provenance.json").write_text(json.dumps({
            "disease": args.disease, "genome_build": "GRCh37/hg19", "source_url": model["url"],
            "weights_zip_sha256": model["zip_sha256"], "weights_member": model["member"],
            "required_variants": model["count"], "validation": "draft",
            "formula": "sum(effect_allele_dosage * effect_weight)",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    except InputError as e:
        return write_failure(out, manifest, [e.problem])
    except (ResourceError, zipfile.BadZipFile) as e:
        return write_failure(out, manifest, [skillkit.Problem("weights", "公开权重", "resource", str(e))], code=2)


if __name__ == "__main__":
    raise SystemExit(main())

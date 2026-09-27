import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


def listed(body):
    grab = False
    rows = []
    for line in body.splitlines():
        if line.startswith("## "):
            if grab:
                break
            grab = line == "## 方法算出的名单"
            continue
        if grab:
            rows.append(line)
    return rows


def run(tmp_path, measurements, labs=True):
    meas = tmp_path / "measurements.csv"
    meas.write_text(measurements, encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    lab = None
    if labs:
        lab = tmp_path / "labs.csv"
        lab.write_text("项目,结果,单位\n血红蛋白,90,g/L\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, lab, 60).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, 60).read_text(encoding="utf-8")
    assert text.endswith(f"边界: {BOUNDARY}\n")
    assert "不能据此停" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert listed(text) == listed(bare)
    if labs:
        assert "血红蛋白 90 g/L" in text
    return text


from presets import AOB_COUNT, EPITOC2, tnsc


def test_one_probe_matches_formula(tmp_path: Path):
    assert AOB_COUNT == 413
    assert len(EPITOC2) == 163
    probe, delta, beta0 = EPITOC2[0]
    assert probe == "cg00043095"
    beta = beta0 + delta * (1 - beta0)
    assert abs(tnsc({probe: beta})[0] - 2) < 1e-9
    text = run(tmp_path, f"name,value\n{probe},{beta}\n")
    rows = listed(text)
    assert rows[0].startswith("1. epiTOC2")
    assert "tnsc 是 2.0000" in rows[0]
    assert "irS" in rows[0]
    assert "不是克隆性造血" in rows[0]

def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "## 方法算出的名单" in text
    assert "## 你正在使用的药" in text
    assert "没有提供现用药" in text
    assert "## 体检" in text
    assert "体检不增删" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"



# Rows given to OmniAgePy 0.99.5 (git 220ef91) as one sample: 150 of the 163
# epiTOC2 probes, 40 of them NaN, 13 probes absent. Betas are random draws in
# [0, 0.3]; they are a cross-check input, not data from the paper.
OMNIAGEPY_ROWS = """\
cg00043095,NA
cg00347369,NA
cg00397986,NA
cg00466268,NA
cg00884606,NA
cg00916884,NA
cg01435574,NA
cg01537995,NA
cg01587896,NA
cg01699217,NA
cg01783070,NA
cg01830294,NA
cg02150988,NA
cg02186542,NA
cg02266732,NA
cg02631468,NA
cg02726121,NA
cg02796545,NA
cg02964724,NA
cg03045635,NA
cg03111498,NA
cg03140968,NA
cg03181582,NA
cg03430846,NA
cg03450948,NA
cg03603951,NA
cg03874199,NA
cg04188273,NA
cg04408488,NA
cg04431946,NA
cg04549460,NA
cg04597433,NA
cg04633225,NA
cg04672706,NA
cg04902729,NA
cg04996219,NA
cg05093169,NA
cg05099387,NA
cg05182249,NA
cg05344430,NA
cg05446424,0.19239845074181247
cg05666607,0.25578985154419703
cg05886671,0.1778823054312852
cg06469345,0.07802923432116696
cg06672560,0.2519644563094226
cg06987468,0.15284876445645282
cg07195011,0.1532666653399599
cg07315745,0.22590906231065336
cg07357987,0.04437661073548697
cg07557260,0.2458880157357831
cg07621749,0.20498607180097714
cg07897248,0.2361290824664403
cg07950000,0.05748487770604057
cg08073312,0.240709248340359
cg08074851,0.05739717781716008
cg08448701,0.024465785209053813
cg08530317,0.25656809228612104
cg08834401,0.2583850488533005
cg08961408,0.26296112892497414
cg09578028,0.14157291580763706
cg10094616,0.08221451658411548
cg10281002,0.0021275485809498784
cg10343742,0.19371626867248434
cg10406295,0.2159728150526079
cg10824063,0.2506707649500822
cg11334771,0.08456334820936263
cg11354629,0.06456545014889208
cg11723848,0.19179941401997636
cg11848563,0.2415164499435029
cg12071328,0.2891012618534913
cg12180703,0.04515744912635324
cg12417685,0.14466371645980095
cg12743978,0.26841475865885206
cg12882697,0.1268150720836312
cg13078140,0.17685061862521442
cg13177747,0.00734720324800896
cg13281139,0.20203796614588168
cg13368756,0.27572658589014676
cg13526007,0.2480475988670163
cg14456683,0.265656080012984
cg14473102,0.198106614156157
cg14717170,0.07366568017295327
cg14769207,0.2305550996688763
cg14834938,0.06350242278225315
cg14991487,0.24938245039933835
cg15119027,0.018815376771230474
cg15186181,0.24764634401806673
cg15237923,0.04935217994223039
cg15272362,0.11254409894899255
cg15493780,0.09502144996708929
cg15984718,0.20740111058332236
cg16023545,0.05357156345231157
cg16033053,0.11887684866509593
cg16523380,0.0017473785323942836
cg16800165,0.07874841382503045
cg17037282,0.12635664426868656
cg17076890,0.03177637101219733
cg17152757,0.18994798381096734
cg17339147,0.1141272809659597
cg17371081,0.21758818142287165
cg17412886,0.1961598033205183
cg17816908,0.12936802463322186
cg17863912,0.26019615169265975
cg18097532,0.18964053525005012
cg18369866,0.2430823056318897
cg18498593,0.1025384171820339
cg19042459,0.16310078690053667
cg19054524,0.05888906553442602
cg19180624,0.29884235703558837
cg19283196,0.07296463929189813
cg19346645,0.07706024016813082
cg19384289,0.021957021717289794
cg19401340,0.07734093569902097
cg19542816,0.22893855976321595
cg19711579,0.2093680712049244
cg19712603,0.03860196369515083
cg19761848,0.11287155042842827
cg20097440,0.12627641838523887
cg20585530,0.1994952739085882
cg20720059,0.13677868891312464
cg20926035,0.17595549804765942
cg21053529,0.2519053810826827
cg21269843,0.21794208309371113
cg21426003,0.10950217905256768
cg21517947,0.13451889280334528
cg21859781,0.11030987090700198
cg22240472,0.03292039920200902
cg22274395,0.06097246322621897
cg22277994,0.08514194668323932
cg22428147,0.09424016868069066
cg22600043,0.0939143576459813
cg22653976,0.1730099148758856
cg22797735,0.2915069926859264
cg23132624,0.23239924047711957
cg23217126,0.23734018445184157
cg23335460,0.22778055016187398
cg23405575,0.17909631915712693
cg23420260,0.2753076771512738
cg23774356,0.20688904663412427
cg23847712,0.15010692922106128
cg24154839,0.023125142550161626
cg24319902,0.14653476812565716
cg24891539,0.0638492986021003
cg24989962,0.039808889264036175
cg25116388,0.15181947675881188
cg25307168,0.2355255877790877
cg25599538,0.08850193284165583
cg25640822,0.23063152797274994
cg25682299,0.1576888569486762
cg25951981,0.044714407011213764
"""
OMNIAGEPY_TNSC = 5178.103879364018
OMNIAGEPY_IRS_55 = 94.14734326116397


def _report(tmp_path, body, age=55):
    """Report for one measurements file at the given age, with the shared boundary checks."""
    meas = tmp_path / "measurements.csv"
    meas.write_text(body, encoding="utf-8")
    path, code = personal_report.run(tmp_path / "out", meas, None, None, age)
    text = path.read_text(encoding="utf-8")
    assert code == 0
    assert text.endswith(f"边界: {BOUNDARY}\n")
    return text


def _score_line(text):
    rows = listed(text)
    assert rows and rows[0].startswith("1. epiTOC2")
    return rows[0]


def _refused(tmp_path, name, body, age=55):
    meas = tmp_path / name
    meas.write_text(body, encoding="utf-8")
    path, code = personal_report.run(tmp_path / ("out_" + name), meas, None, None, age)
    text = path.read_text(encoding="utf-8")
    assert code == 3
    assert "这次没有计算" in text
    assert "tnsc" not in text
    assert text.endswith(f"边界: {BOUNDARY}\n")
    return text


def test_matches_omniagepy_epitoc2_without_na_rows(tmp_path: Path):
    """Matches OmniAgePy EpiTOC2.predict(ages=[55]) on the same input (a cross-check, not a paper-printed value)."""
    numeric = "".join(line + "\n" for line in OMNIAGEPY_ROWS.splitlines() if not line.endswith(",NA"))
    observed = {}
    for line in numeric.splitlines():
        probe, value = line.split(",")
        observed[probe] = float(value)
    score, used = tnsc(observed)
    assert used == 110
    assert abs(score - OMNIAGEPY_TNSC) < 1e-6
    assert abs(score / 55 - OMNIAGEPY_IRS_55) < 1e-8
    text = _report(tmp_path, "name,value\n" + numeric)
    line = _score_line(text)
    assert "163 个探针里用了 110 个" in line
    assert "tnsc 是 5178.1039" in line
    assert "irS = tnsc / 55 = 94.1473" in line
    assert "空值或 NA" not in line


def test_na_rows_are_skipped_like_omniagepy(tmp_path: Path):
    """The 40 NA rows are what OmniAgePy's NaN-skipping mean ignores; same tnsc as above."""
    lines = OMNIAGEPY_ROWS.splitlines()
    assert all(line.endswith(",NA") for line in lines[1:4])
    lines[1] = lines[1].replace(",NA", ",")      # blank
    lines[2] = lines[2].replace(",NA", ",nan")   # nan
    lines[3] = lines[3].replace(",NA", ",N/A")
    text = _report(tmp_path, "name,value\n" + "\n".join(lines) + "\n")
    line = _score_line(text)
    assert "163 个探针里用了 110 个，另有 40 个在文件里是空值或 NA，按缺失跳过" in line
    assert "tnsc 是 5178.1039" in line
    assert "irS = tnsc / 55 = 94.1473" in line
    assert "nan" not in text.lower()


def test_only_na_rows_give_no_score(tmp_path: Path):
    text = _report(tmp_path, "name,value\ncg00043095,NA\ncg00347369,\n")
    assert "都是空值或 NA，所以没有总干细胞分裂数" in text
    assert [row for row in listed(text) if row] == ["没有项目进入名单。"]
    assert "nan" not in text.lower()


def test_probe_names_match_without_case(tmp_path: Path):
    probe, delta, beta0 = EPITOC2[0]
    beta = beta0 + delta * (1 - beta0)
    text = run(tmp_path, f"name,value\n{probe.upper()},{beta}\n")
    assert "tnsc 是 2.0000" in _score_line(text)


def test_tab_separated_file_is_read(tmp_path: Path):
    probe, delta, beta0 = EPITOC2[0]
    beta = beta0 + delta * (1 - beta0)
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    headed = run(tmp_path / "a", f"name\tvalue\n{probe}\t{beta}\n")
    bare = run(tmp_path / "b", f"{probe}\t{beta}\n")
    assert "tnsc 是 2.0000" in _score_line(headed)
    assert "tnsc 是 2.0000" in _score_line(bare)


def test_percent_values_are_refused(tmp_path: Path):
    text = _refused(tmp_path, "pct.csv", "name,value\ncg00043095,45\ncg00347369,12.5\n")
    assert "看起来像百分比" in text
    assert "不替你换算" in text


def test_m_values_are_refused(tmp_path: Path):
    text = _refused(tmp_path, "mval.csv", "name,value\ncg00043095,-3.2\ncg00347369,-2.5\n")
    assert "看起来像 M 值" in text


def test_duplicate_probe_is_refused_even_across_case(tmp_path: Path):
    text = _refused(tmp_path, "dup.csv", "name,value\ncg00043095,0.1\nCG00043095,0.1\n")
    assert "出现了不止一次" in text


def test_unreadable_value_and_bad_layout_are_refused(tmp_path: Path):
    text = _refused(tmp_path, "abc.csv", "name,value\ncg00043095,abc\n")
    assert "cg00043095「abc」" in text
    text = _refused(tmp_path, "space.csv", "cg00043095 0.1\n")
    assert "只有一列" in text


def test_age_must_be_above_zero(tmp_path: Path):
    text = _refused(tmp_path, "age.csv", "name,value\ncg00043095,0.1\n", age=0)
    assert "年龄要大于 0" in text


def test_command_line_exit_code(tmp_path: Path):
    import subprocess
    meas = tmp_path / "pct.csv"
    meas.write_text("name,value\ncg00043095,45\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "personal_report.py"), "--measurements", str(meas), "--out", str(tmp_path / "cli")],
        capture_output=True, text=True,
    )
    assert result.returncode == 3
    assert (tmp_path / "cli" / "problems.json").exists()

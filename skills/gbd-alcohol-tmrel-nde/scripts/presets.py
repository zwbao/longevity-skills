"""Table S1 values and Figure 1 unit definition, GBD 2020 Alcohol Collaborators."""
import csv
import math
from functools import lru_cache
from pathlib import Path

ALCOHOL_KEY = "ethanol_g_day"
ALCOHOL_UNIT = "g/d"
ALCOHOL_RANGE = (0, 100)  # Methods: risk curves evaluated over 0–100 g/day.
GRAMS_PER_STANDARD_DRINK = 10  # Main article Figure 1 and Figure 3 captions.
YEARS = (1990, 2000, 2010, 2020)  # Appendix 2, Table S1.
VALUE_KEYS = ("tmrel_standard_drinks_day", "tmrel_ui_low", "tmrel_ui_high",
              "nde_standard_drinks_day", "nde_ui_low", "nde_ui_high")
BOUNDARY = ("这是个人摄入量与历史人群模型阈值的比较，不是个人患病概率、安全饮酒量或饮酒目标；"
            "不能据此开始或增加饮酒，也不能据此开始或停止药物。模型未区分集中大量饮酒与分散饮酒，"
            "未按个人疾病、用药、妊娠或遗传因素调整。")
REGION_ZH = {
    "Central Asia": "中亚", "Central Europe": "中欧", "Eastern Europe": "东欧",
    "Australasia": "澳大拉西亚", "High-income Asia Pacific": "高收入亚太",
    "High-income North America": "高收入北美", "Southern Latin America": "拉丁美洲南部",
    "Western Europe": "西欧", "Andean Latin America": "安第斯拉丁美洲", "Caribbean": "加勒比",
    "Central Latin America": "拉丁美洲中部", "Tropical Latin America": "热带拉丁美洲",
    "North Africa and Middle East": "北非和中东", "South Asia": "南亚", "East Asia": "东亚",
    "Oceania": "大洋洲", "Southeast Asia": "东南亚", "Central Sub-Saharan Africa": "撒哈拉以南非洲中部",
    "Eastern Sub-Saharan Africa": "撒哈拉以南非洲东部", "Southern Sub-Saharan Africa": "撒哈拉以南非洲南部",
    "Western Sub-Saharan Africa": "撒哈拉以南非洲西部",
}


def normalize_region(region):
    for english, chinese in REGION_ZH.items():
        if str(region).strip().casefold() in (english.casefold(), chinese):
            return english
    raise ValueError("请选择表 S1 的 GBD 地区；可用 --list-regions 查看，不把国家名或全球平均当成地区。")


def normalize_sex(sex):
    aliases = {"male": "male", "m": "male", "男": "male", "female": "female", "f": "female", "女": "female"}
    try:
        return aliases[str(sex).strip().casefold()]
    except KeyError:
        raise ValueError("论文分层性别需为 male/男 或 female/女；不能合并两列。") from None


@lru_cache(maxsize=1)
def table():
    with (Path(__file__).resolve().parents[1] / "data/table_s1.csv").open(encoding="utf-8") as handle:
        rows = {}
        for row in csv.DictReader(handle):
            row.update({k: float(row[k]) for k in VALUE_KEYS})
            row["year"] = int(row["year"])
            rows[(row["region"], row["age_group"], row["year"], row["sex"])] = row
    return rows


def lookup(region, age, sex, year):
    region, sex = normalize_region(region), normalize_sex(sex)
    if not math.isfinite(float(age)) or not 15 <= age <= 120:
        raise ValueError("年龄须在 15–120 岁内；80 岁及以上只使用表 S1 的 80 plus 合并档。")
    if year not in YEARS:
        raise ValueError("只支持表 S1 印出的 1990、2000、2010、2020 年，不插值或外推。")
    low = int(age // 5) * 5
    age_group = "80 plus" if age >= 80 else f"{low} to {low + 4}"
    return dict(table()[(region, age_group, year, sex)])

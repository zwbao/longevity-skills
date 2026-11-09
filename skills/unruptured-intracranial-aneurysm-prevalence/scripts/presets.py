"""Every number the report uses, copied from Dremel et al., Lancet Neurol 2026;25:911-925.

Locators: "Results" is the main-text Results section, "Table 2" the main-text
table, "Appendix" the supplementary appendix (mmc1, 40 pages). Values are the
pooled estimates as printed (one decimal); nothing here is recomputed.
Each tuple is (point, low, high) of the printed 95% CI.
"""

from __future__ import annotations

# Results, studies in healthy individuals: "The estimated prevalence in the reference
# population (without comorbidities, 50% women, and mean age 50 years) was 3·9% (3·0–5·1, 0·9–14·3)."
REFERENCE_PREVALENCE = (3.9, 3.0, 5.1)
REFERENCE_PREDICTION_INTERVAL = (0.9, 14.3)

# Results: "The prevalence was 2·9% (1·7–4·5) in cohorts younger than 55 years and
# 5·2% (3·4–7·0) in cohorts older than 55 years." Appendix S2: study populations were
# dichotomised by the age "that divided the study populations in half, i.e. over and under 55".
# These are study populations grouped by their average age, not individuals.
AGE_CUTOFF = 55
AGE_BANDS = {
    "under_55": {"label_zh": "平均年龄 55 岁以下的研究人群", "prevalence": (2.9, 1.7, 4.5)},
    "over_55": {"label_zh": "平均年龄 55 岁以上的研究人群", "prevalence": (5.2, 3.4, 7.0)},
}
# Results: "a relative increase of 1·06% (95% CI 1·03–1·09) in UIA prevalence per additional
# year of age". Quoted as printed; the notation (percent or ratio) is ambiguous, so it is not
# used to compute anything.
AGE_PER_YEAR_PRINTED = "1·06%（95% CI 1·03–1·09）"

# Results: "The crude prevalence for women was 5·5% (95% CI 4·3–6·9, 3415 of 65020 participants)
# and 3·0% (2·2–4·0, 2122 of 76130 participants) for men (RR for women 1·9 [95% CI 1·8–2·0])."
SEX = {
    "female": {"prevalence": (5.5, 4.3, 6.9), "events": 3415, "total": 65020},
    "male": {"prevalence": (3.0, 2.2, 4.0), "events": 2122, "total": 76130},
}
RR_FEMALE = (1.9, 1.8, 2.0)

# Results: "The RR for current smoking compared with non-smoking was 1·4 (1·2–1·6)."
# Appendix S2: non-smokers are "never or previous smokers, according to the definition in the parent paper".
RR_CURRENT_SMOKING = (1.4, 1.2, 1.6)
# Results: "The RR for UIA for any smoking compared with non-smoking was 1·14 (1·07–1·22)."
RR_ANY_SMOKING = (1.14, 1.07, 1.22)

# Results: "The RR for any definition of hypertension compared with no hypertension was 1·6 (1·5–1·7)."
RR_HYPERTENSION = (1.6, 1.5, 1.7)
# Appendix S3: hypertension defined as antihypertensive medication or blood pressure >140/90 mmHg,
# 7 studies: "The RR was 1·3 (95%CI:1·2-1·4)."
RR_HYPERTENSION_STRICT = (1.3, 1.2, 1.4)

# Table 2 (crude prevalence, crude PR, PR adjusted for age and sex = last column) and
# Appendix Table 5 (GRADE certainty). Definitions from Appendix S1.
GROUPS = {
    "adpkd": {
        "label_zh": "常染色体显性多囊肾病（ADPKD）",
        "events": 293, "total": 1990,
        "prevalence": (12.8, 9.2, 17.6),
        "pr_crude": (4.2, 2.4, 7.2),
        "pr_adjusted": (4.4, 1.5, 12.6),
        "grade_zh": "中等",
    },
    "connective_tissue": {
        "label_zh": "结缔组织病（马方、埃勒斯-当洛斯、Loeys-Dietz 综合征合并）",
        "events": 94, "total": 879,
        "prevalence": (10.3, 6.5, 16.0),
        "pr_crude": (3.3, 1.8, 6.2),
        "pr_adjusted": (3.9, 2.0, 7.6),
        "grade_zh": "很低",
    },
    "family_history": {
        "label_zh": "一级亲属有动脉瘤性蛛网膜下腔出血或未破裂颅内动脉瘤",
        "events": 412, "total": 4252,
        "prevalence": (7.9, 5.6, 11.1),
        "pr_crude": (2.5, 1.5, 4.0),
        "pr_adjusted": (2.4, 0.5, 11.2),
        "grade_zh": "很低",
    },
    "atherosclerosis": {
        "label_zh": "动脉粥样硬化相关病（颈动脉狭窄、缺血性卒中、缺血性心脏病等）",
        "events": 2229, "total": 40970,
        "prevalence": (5.5, 4.7, 6.4),
        "pr_crude": (1.7, 1.2, 2.4),
        "pr_adjusted": (1.3, 0.8, 2.0),
        "grade_zh": "中等",
    },
}

# Results, sensitivity analysis on family history: one affected relative 6·7% (4·0-10·9),
# two or more affected family members 9·5% (7·9–11·4).
FAMILY_SUBGROUPS = {
    "one": {"label_zh": "家里只有一位亲属患病（一级亲属）", "prevalence": (6.7, 4.0, 10.9)},
    "two_or_more": {"label_zh": "家里有两位及以上亲属患病（一级亲属）", "prevalence": (9.5, 7.9, 11.4)},
}

# Appendix Table 6, studies on healthy individuals: crude prevalence, crude PR and the
# age-and-sex adjusted PR (last column), USA as reference. Main text: "There were no
# significant differences in UIA prevalence according to country after adjustment for age and sex".
COUNTRIES = {
    "china": {"label_zh": "中国", "events": 701, "total": 10689, "prevalence": (8.5, 6.0, 11.8),
              "pr_crude": (3.7, 1.4, 9.7), "pr_age_sex": (2.1, 1.0, 4.2)},
    "japan": {"label_zh": "日本", "events": 1799, "total": 34138, "prevalence": (3.7, 2.3, 5.7),
              "pr_crude": (1.4, 0.6, 3.3), "pr_age_sex": (1.1, 0.5, 2.1)},
    "south_korea": {"label_zh": "韩国", "events": 1842, "total": 68791, "prevalence": (3.2, 2.3, 4.5),
                    "pr_crude": (1.3, 0.5, 3.3), "pr_age_sex": (0.5, 0.3, 1.1)},
    "usa": {"label_zh": "美国", "events": 2790, "total": 62058, "prevalence": (2.0, 0.8, 5.1),
            "pr_crude": None, "pr_age_sex": None},
    "finland": {"label_zh": "芬兰", "events": 133, "total": 1995, "prevalence": (6.7, 5.7, 7.9),
                "pr_crude": (2.2, 0.5, 9.0), "pr_age_sex": (0.9, 0.2, 3.0)},
    "germany": {"label_zh": "德国", "events": 219, "total": 5476, "prevalence": (0.4, 0.0, 21.8),
                "pr_crude": (0.4, 0.1, 1.6), "pr_age_sex": (0.7, 0.2, 2.3)},
    # The printed CI for the Netherlands is "01·0-1·5", which cannot bracket 2·1%; it is not shown.
    "netherlands": {"label_zh": "荷兰", "events": 175, "total": 8142, "prevalence": (2.1, None, None),
                    "pr_crude": (0.8, 0.2, 2.8), "pr_age_sex": (0.3, 0.1, 0.8)},
    "uk": {"label_zh": "英国", "events": 43, "total": 1305, "prevalence": (2.0, 0.7, 5.4),
           "pr_crude": (0.7, 0.2, 2.7), "pr_age_sex": (0.6, 0.2, 1.9)},
}
COUNTRY_ALIASES = {
    "china": ["china", "cn", "中国", "中国大陆", "prc"],
    "japan": ["japan", "jp", "日本"],
    "south_korea": ["south korea", "korea", "kr", "韩国", "南韩"],
    "usa": ["usa", "us", "united states", "america", "美国"],
    "finland": ["finland", "fi", "芬兰"],
    "germany": ["germany", "de", "德国"],
    "netherlands": ["netherlands", "nl", "holland", "荷兰"],
    "uk": ["uk", "united kingdom", "britain", "gb", "英国"],
}

# Results: studies in healthy individuals with MR or CT angiography, mid-year of data
# acquisition 2016-2022: 6·6% (6·3–6·8); 2002-2015: 2·9% (2·8–3·0); age and sex adjusted PR 1·8 (1·1–2·8).
RECENT_IMAGING = {"2002_2015": (2.9, 2.8, 3.0), "2016_2022": (6.6, 6.3, 6.8), "pr_age_sex": (1.8, 1.1, 2.8)}

BOUNDARY = ("这些是论文汇总的人群患病率（某一类人里多少人在影像或尸检中查到未破裂颅内动脉瘤），"
            "不是你本人有没有动脉瘤的判断；几项比值不能相乘成你的个人概率；"
            "它不决定要不要做筛查、做哪种检查，也不决定开始或停止任何药物。")

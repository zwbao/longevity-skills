"""Printed lookup contract: Belloy et al., JAMA Neurology 2023."""
TITLE = "APOE 基因型与阿尔茨海默病分层关联"
BOUNDARY = "这是研究人群相对 APOE ε3/ε3 的关联查表，不是个人患病绝对概率、诊断或治疗建议；不能据此开始、停用或调整药物。"
INPUT_UNITS = {"age": "a", "ancestry_percent": "%"}
# Main Methods: older than 55; eMethods p.11: minimum 55. Use the intersection.
AGE_MIN_EXCLUSIVE = 55
# Operational input sanity bound, NOT a published inclusion maximum.
AGE_SANITY_MAX = 120
# eMethods p.11 removes ages censored at 90+. Conservative product restriction.
SURVIVAL_AGE_MAX_EXCLUSIVE = 90
# eTable16 title/column header uses >75%, despite >=75% in ancestry QC methods.
ANCESTRY_MIN_EXCLUSIVE = 75
GENOTYPES = ("22", "23", "24", "33", "34", "44")
GROUPS = {"nhw": "非西班牙裔白人", "nhb": "非西班牙裔黑人",
          "hispanic": "西班牙裔（含各种族）", "east_asian": "东亚研究样本（日本、韩国）"}
ANCESTRIES = {"european": "全基因组欧洲祖源", "african": "全基因组非洲祖源",
              "amerindian": "全基因组美洲原住民祖源"}
SEX_LABELS = {"male": "男性", "female": "女性", "pooled": "男女合并"}

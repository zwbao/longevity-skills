"""Wood et al., Lancet 2018: printed constants, never fitted from curves."""
ALCOHOL_KEY = 'alcohol_g_week'
# Mass consumed over one week; period is in key/label, unit is mass (schema/units.json).
ALCOHOL_UNIT = 'g'
GRAMS_PER_UK_UNIT = 8  # Methods p1515 and Appendix Annex 1 p1.
# Figure 4 and Results p1520: baseline REPORTED amounts, not usual means.
BANDS = (
    (100, '>0–≤100 g/week', '参照档；未给此档相对不饮酒者的寿命差'),
    (200, '>100–≤200 g/week', '约6个月'),
    (350, '>200–≤350 g/week', '约1–2年'),
    (None, '>350 g/week', '约4–5年'),
)
TITLE = '每周饮酒量的研究分档'
BOUNDARY = ('边界：这是高收入国家当前饮酒且无既往心血管病人群的观察性关联；'
            '约100克/周不是安全线或建议摄入量，不支持不饮酒者开始饮酒。'
            '40岁寿命差是研究人群的模型估计，不是你的寿命损失，也不是改变饮酒量能获得的寿命收益；'
            '不据此开始、停止或调整药物。')

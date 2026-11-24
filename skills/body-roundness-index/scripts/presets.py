"""Thomas et al., Obesity 2013, DOI 10.1002/oby.20408.

BRI constants: main text, Methods / Body Roundness Index.
Eccentricity geometry: Supplemental Information pp. 30–34, Figure S1.
Input plausibility ranges are engineering checks, not clinical cutoffs.
"""
BRI_OFFSET = 364.2
BRI_SCALE = 365.5
MEASUREMENTS = (('height_cm', '身高', 'cm'), ('waist_cm', '腰围', 'cm'))
BOUNDARY = 'BRI 是身高与腰围构成的体形指标，不是体脂率、内脏脂肪量、疾病风险或寿命预测；不能据此判断健康与否、制定减重目标或开始、停止药物。'

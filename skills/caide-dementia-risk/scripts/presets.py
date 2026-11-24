"""Kivipelto et al., Lancet Neurology 2006, pp 736–738, Tables 2–4."""
TITLE = 'CAIDE 中年痴呆风险评分'
BOUNDARY = ('这是芬兰中年队列的观察性风险模型，适用于基线 39–64 岁且存活至晚年复查的人群；'
            '不能诊断痴呆，也不是你必然发病的概率。目标情景的数值变化不是干预效果，'
            '不能据此开始或停用药物。')
INPUT_UNITS = {'education_years':'a', 'sbp_mmhg':'mmHg', 'bmi_kg_m2':'kg/m^2',
               'total_cholesterol_mmol_l':'mmol/L', 'physical_active_1':'1',
               'apoe_e4_1':'1', 'age':'a', 'sex':None}
# Printed categories and scores: (label, score), in ascending numerical input order.
CATEGORIES = {
 'basic': {
  'age':[('<47',0),('47–53',3),('>53',4)],
  'education_years':[('0–6',3),('7–9',2),('≥10',0)],
  'sex':[('female',0),('male',1)],
  'sbp_mmhg':[('≤140',0),('>140',2)],
  'bmi_kg_m2':[('≤30',0),('>30',2)],
  'total_cholesterol_mmol_l':[('≤6.5',0),('>6.5',2)],
  'physical_active_1':[('Inactive',1),('Active',0)],
 },
 'apoe': {
  'age':[('<47',0),('47–53',3),('>53',5)],
  'education_years':[('0–6',4),('7–9',3),('≥10',0)],
  'sex':[('female',0),('male',1)],
  'sbp_mmhg':[('≤140',0),('>140',2)],
  'bmi_kg_m2':[('≤30',0),('>30',2)],
  'total_cholesterol_mmol_l':[('≤6.5',0),('>6.5',1)],
  'physical_active_1':[('Inactive',1),('Active',0)],
  'apoe_e4_1':[('Non–ε4',0),('ε4',2)],
 }}
AGE_CUTOFFS = (47,53)
EDUCATION_CUTOFFS = (6,9)
BINARY_CUTOFFS = {'sbp_mmhg':140, 'bmi_kg_m2':30, 'total_cholesterol_mmol_l':6.5}
# Methods p736: beta1 is ALREADY the 20-year contribution; do not multiply by 20.
LOGISTIC = {'basic':(-7.406,0.796,0.401), 'apoe':(-8.083,1.020,0.390)}
# Table 3: lower/upper score, group incidence %, printed 95% CI endpoints %.
GROUPS = {'basic':[(0,5,1.0,0.0,2.0),(6,7,1.9,0.2,3.5),(8,9,4.2,1.9,6.4),
                   (10,11,7.4,4.1,10.6),(12,15,16.4,9.7,23.1)],
          'apoe':[(0,5,0.3,-0.3,1.0),(6,8,1.7,0.3,3.0),(9,10,4.6,2.0,7.1),
                  (11,12,4.4,1.7,7.1),(13,18,16.3,10.7,21.9)]}
MODIFIABLE = {'sbp_mmhg','bmi_kg_m2','total_cholesterol_mmol_l','physical_active_1'}
SCENARIO_NOTE = ('仅替换输入后重新计算同一个模型；不是降低痴呆风险的因果预测。'
                 '评分是阶梯函数，敏感度列出每项跨分档的变化；不提供伪连续导数。'
                 '年龄、性别、已完成教育年限和基因型不作为干预目标。')

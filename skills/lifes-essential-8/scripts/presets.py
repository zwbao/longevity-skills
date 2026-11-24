"""Lloyd-Jones et al., Circulation 2022, Table 1 and implementation notes.
Each pair is (inclusive lower bound, points); no coefficients are fitted.
"""
METRICS = ('diet','activity','nicotine','sleep','bmi','lipids','glucose','bp')
LABELS = ('饮食','体力活动','尼古丁暴露','睡眠','体质指数','血脂','血糖','血压')
DIET = ((0,0),(4,25),(8,50),(12,80),(15,100))
ACTIVITY = ((0,0),(1,20),(30,40),(60,60),(90,80),(120,90),(150,100))
SLEEP = ((0,0),(4,20),(5,40),(6,70),(7,100),(9,90),(10,40))
BMI = ((18.5,100),(25,70),(30,30),(35,15),(40,0))
BMI_ASIAN = ((18.5,100),(23,75),(25,50),(30,25),(35,0))
LIPIDS = ((0,100),(130,60),(160,40),(190,20),(220,0))
A1C_DIABETES = ((0,40),(7,30),(8,20),(9,10),(10,0))
SBP = ((0,100),(120,75),(130,50),(140,25),(160,0))
DBP = ((0,100),(80,50),(90,25),(100,0))
NICOTINE = (100,75,50,25,0)  # never; quit >=5y; quit 1–<5y; quit <1y; current
PENALTY = 20
N_METRICS = 8
VIGOROUS_WEIGHT = 2
CATEGORY = ((0,'低'),(50,'中等'),(80,'高'))
FBG_NORMAL = 100
FBG_UNCLASSIFIED = 126
A1C_NORMAL = 5.7
A1C_UNCLASSIFIED = 6.5
INPUT_UNITS = {
 'mepa_score':'score', 'moderate_min_week':'min', 'vigorous_min_week':'min',
 'smoking_status':'1','inhaled_nicotine':'1','indoor_smoke':'1','sleep_h':'h',
 'bmi_kg_m2':'kg/m^2','bmi_asian_scale':'1','non_hdl_mg_dl':'mg/dL',
 'lipid_treated':'1','diabetes':'1','fasting_glucose_mg_dl':'mg/dL','hba1c_pct':'%',
 'sbp_mmhg':'mmHg','dbp_mmhg':'mmHg','bp_treated':'1',
 'sleep_apnea_penalty':'1','prediabetes_penalty':'1',
}
FLAGS = tuple(k for k,u in INPUT_UNITS.items() if u=='1' and k!='smoking_status')
TARGET_KEYS = {'mepa_score','moderate_min_week','vigorous_min_week','sleep_h',
               'bmi_kg_m2','non_hdl_mg_dl','fasting_glucose_mg_dl','hba1c_pct',
               'sbp_mmhg','dbp_mmhg'}

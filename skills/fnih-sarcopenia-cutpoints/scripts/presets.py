"""Studenski et al., J Gerontol A 2014, Table 3. All comparisons are strict <."""
CUTPOINTS = {
    "male": {"grip_max_kg": 26, "grip_bmi": 1.0, "alm_bmi": 0.789, "alm_kg": 19.75},
    "female": {"grip_max_kg": 16, "grip_bmi": 0.56, "alm_bmi": 0.512, "alm_kg": 15.02},
}
MIN_AGE = 65  # Results: participants younger than 65 were excluded.
# Input plausibility guards are implementation choices, NOT diagnostic thresholds
# or observed cohort ranges. The paper does not give a maximum eligible age.
INPUT_RANGES = {"grip_max_kg": (0, 150), "alm_kg": (1, 80),
                "bmi_kg_m2": (10, 80), "age": (MIN_AGE, 120)}
INPUT_UNITS = {"grip_max_kg": "kg", "alm_kg": "kg", "bmi_kg_m2": "kg/m^2", "age": "a"}
BOUNDARY = "本报告仅按 FNIH 2014 研究切点描述握力和四肢瘦体重，不诊断肌少症，不估算个人失能或死亡概率，也不能据此开始、停用或调整药物。"

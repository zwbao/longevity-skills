"""Millwood et al., Lancet 2019. Printed constants, not fitted values."""

# Supplementary appendix p 25, Webtable 12, Men Model 1, final row:
# RR (95% CI) per 280 g/week genotype-predicted mean male intake.
STROKE_RR = {
    "ischaemic_stroke": (1.27, 1.13, 1.43),
    "intracerebral_haemorrhage": (1.58, 1.36, 1.84),
    "total_stroke": (1.38, 1.26, 1.51),
}
LABELS = {
    "ischaemic_stroke": "缺血性卒中",
    "intracerebral_haemorrhage": "脑内出血",
    "total_stroke": "总卒中",
}
REFERENCE_WEEKLY_DIFFERENCE_G = 280.0
DAYS_PER_WEEK = 7  # Exact calendar conversion, not an estimated coefficient.
# Webtable 12 Model 1 category mean values; main-text rounded range is 4–256.
GENETIC_CATEGORY_RANGE_G_WEEK = (4, 255)
AGE_RANGE = (30, 79)  # Supplementary methods p 5: baseline age groups.
INTAKE_RANGE = (0, 200)  # Engineering plausibility guard, NOT a safe intake range.
INTAKE_KEYS = ("alcohol_g_day", "reference_alcohol_g_day")
INPUT_UNITS = {"alcohol_g_day": "g/d", "reference_alcohol_g_day": "g/d",
               "age": "a", "prior_cvd": "1"}

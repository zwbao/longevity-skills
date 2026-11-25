"""Mitnitski et al., TheScientificWorldJournal 2001, pp. 324–329.

All model constants are printed in the article. Numerical convergence settings
are implementation precision settings, not fitted or inferred coefficients.
"""

MAX_ITEMS = 92  # Methods and Appendix, pp. 324, 335–336
AGE_RANGE = (65, 106)  # clinical sample, p. 324
GAMMA_SHAPE = 1.456  # Equation (3), p. 328
GAMMA_RATE = 0.209  # Equation (3), p. 328: multiplies V in exp(-lambda*V)
HORIZONS_MONTHS = (24, 60)  # worked examples, p. 329
COUNT_INPUTS = (("deficits_count", "1"), ("assessed_count", "1"))

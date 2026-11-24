# Artificial engineering fixture

`synthetic_profiles.csv` contains 16 artificial 50-layer arrays. It contains no
human imaging data and no expected predictions. Tests repeat these arrays to
exercise the published minimum-vertex requirement and compare inference with
an independent evaluation of the author's checkpoint weights. This is not a
printed example, a physiological validation set, or evidence for clinical use.

Generation: for shifts 0,1,2,3 and artificial marrow levels 40,50,70,90, construct
`[0]*3 + [100]*3 + [200]*4 + [30]*5 + [marrow]*7 + [30]*5 + [90]*23`, cyclically
shift by the indicated offset, add uniform [-2,2] noise from NumPy
`default_rng(101499)`, clip to [0,255], and save with `%.12g`. These artificial
values are engineering choices, not fitted coefficients or paper examples.

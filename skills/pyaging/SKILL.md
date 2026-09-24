---
name: pyaging
description: >-
  Runs published biological aging clocks on a user-supplied feature matrix
  with pyaging. Use when the user mentions pyaging, Horvath, Hannum,
  DunedinPACE, GrimAge, PhenoAge, AltumAge, or asks for a clock prediction
  from methylation, expression, chromatin, or blood-chemistry values. Clock
  outputs are model estimates, not a reason to start or stop a treatment.
---

# pyaging

Run [pyaging](https://github.com/lucascamillomd/pyaging) 0.5.2 (`edb1b37`, Camillo, Bioinformatics 2024, doi:10.1093/bioinformatics/btae200). Python 3.11 or newer. Do not copy the library into this repository. Clock weights download from the `pyaging` Hugging Face organization when a clock runs.

This skill predicts from a matrix the user already has. It does not build a literature catalog, and it does not replace the DrugAge ranking in `longevitybench`.

## Run

Rows are samples. Columns are the clock's features (CpG probes, genes, or chemistry analytes). Put sample covariates that are not features in `metadata_cols`.

```bash
uv run --python 3.11 --with pyaging python - << 'PY'
import pandas as pd
import pyaging as pya

df = pd.read_csv("MATRIX.csv", index_col=0)
adata = pya.pp.df_to_adata(df, metadata_cols=["age"])
pya.pred.predict_age(adata, ["horvath2013"])
print(adata.obs.to_csv())
PY
```

`predict_age` writes ages onto `adata.obs` and returns `None`. Keep the names it prints. `pya.utils.show_all_clocks()` lists clocks; do not invent a name that is absent from that list or from the user's request.

DunedinPACE is a pace. The tAge clocks need raw RNA-seq counts, at least two samples, and are differences against the samples predicted together. Say which of those applies when reporting them.

## Command

For one person's matrix, use the script. It checks the matrix, runs the clocks you name, and writes `out/report.md` and `out/result.json`. It needs an interpreter with pyaging and pandas; the harness maps this skill's `runtime: pyaging` to that interpreter.

```bash
python "$SKILL/scripts/personal_report.py" \
  --matrix MATRIX.csv \
  --clocks horvath2013,dunedinpace \
  --age AGE \
  --out out/
```

`MATRIX.csv`: first column the sample name, other columns the clock's features. Methylation values are betas on the 0–1 scale; percentages and M-values are refused, not rescaled. At most 20 samples. `--metadata-cols` names covariate columns that are not features (default `age`). `--data-type other` skips the beta check for expression or chemistry matrices.

Exit code 3 means the matrix did not pass the checks; 4 means pyaging is not installed in this interpreter. Neither case is replaced with an estimated age. `result.json` names the clock outputs `dnam_*` (for example `dnam_phenoage`), because a methylation PhenoAge is not the blood-chemistry phenotypic age of `accelerated-biological-aging-risk`.

## Boundary

Report the clock name, the value column, the sample count, and any warning pyaging printed about missing features or imputation. Do not replace a failed clock with an estimated age. Do not tell the user to start or stop a medicine because a clock moved.

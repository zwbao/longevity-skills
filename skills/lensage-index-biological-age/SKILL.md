---
name: lensage-index-biological-age
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Subtracts chronological age from a lens age the user already has,
  which is how Li et al., Nature Communications 2023 define the LensAge index, and places the
  difference beside the 5, 10, and 20 year fast-ager lines the paper reports. The lens age itself
  comes from the paper's InceptionV3 photo model, whose code is released only on request, so the
  script does not run it or check the lens age. Use when the user mentions LensAge or a lens
  photograph age minus chronological age. Medicines and checkup labs stay context.
---

# 晶状体年龄指数

论文的照片模型要向作者申请，这里不运行它。你交已经得到的晶状体年龄和实足年龄。报告用前者减去后者，并对照大于 5 年、10 年和 20 年这三个快老化切点。两个数缺一个时，报告说明没有算出指数。

不要向用户要照片模型或 PDF。不要另造网络权重。现用药对不上时写「不能据此停」。体检不增删指数。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 50 \
  --out out
```

`lens_age` 和 `chronological_age` 用岁。文件里的实足年龄优先于命令行年龄。

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。

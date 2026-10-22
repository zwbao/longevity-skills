# 例子

论文补充表格的算例（NHANES IV SEQN 10，男，43.1666 岁）把 61 项代进公式，各项之和 7.389850952344081，年龄差 5.370465592344081 岁，LinAge 48.537065592344085 岁；`tests/test_manifest.py` 用同一个人的原始化验值复现到 1e-9 岁。

```csv
item,value,unit
总胆固醇,140,mg/dL
HDL-C,1.31,mmol/L
甘油三酯,0.474,mmol/L
超敏C反应蛋白,1.2,mg/L
血红蛋白,154,g/L
ALT,20,U/L
收缩压,142,mmHg
hypertension,1,
healthcare_visits_past_year,6,
```

```bash
python3 "$SKILL/scripts/personal_report.py" --measurements measurements.csv --age 60 --sex 男 --out out
```

只给了这几项时，其余 50 多项按 0 计，报告会列出这些缺项和它们权重的绝对值之和，这时的 LinAge 很不可靠。

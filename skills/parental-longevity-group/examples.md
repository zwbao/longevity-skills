```bash
python "$SKILL/scripts/personal_report.py" --measurements parents.csv --sex female --age 70 --out out
```

`parents.csv`：

```
item,value,unit
父亲去世时年龄,88,岁
母亲目前年龄,92,岁
```

父亲 88 岁去世、母亲在世 92 岁，两位都活到 85 岁，分组为“高”（high-PL），父母年龄均值 90.0 岁；报告再列出论文里高组与低组相比的差别方向。这是合成输入，论文没有印出个人算例。

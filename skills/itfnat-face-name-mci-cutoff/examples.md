```bash
python "$SKILL/scripts/personal_report.py" --measurements scores.csv --out out
```

`scores.csv`：

```
item,value,unit
ItFNAT DFR adjusted,3.21,score
MoCA adjusted,24,score
```

DFR 校正分 3.21 落在切点 ≤3.21 一侧，阳性似然比 3.086（表 4：60.00/(100−80.56)，正文印 PLR = 3.086）；MoCA 校正分 24 在切点 23.99 以上，阴性似然比 0.485（表 4：35.00/72.22，正文印 NLR = 0.485）。分数是合成输入。

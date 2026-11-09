```bash
python "$SKILL/scripts/personal_report.py" --measurements fitness.csv --sex female --age 78 --targets targets.csv --out out
```

`fitness.csv`：

```
item,value,unit
30秒椅子坐立,9,次
8英尺起身绕行,10.2,秒
```

`targets.csv`：

```
item,value,unit
30秒椅子坐立,16,次
8英尺起身绕行,7.4,秒
```

女性 30 秒椅子坐立 9 次在 Q1（0–10 次，参照组），8 英尺起身绕行 10.2 秒在 Q1（9.01–22.00 秒）；进入上一档的起点是 11 次和 9.00 秒。目标 16 次落在 Q4（eFigure 6 女性风险比 0.56，0.45–0.70），7.4 秒落在 Q3（0.53，0.42–0.65）。这是合成输入，论文没有印出个人算例。

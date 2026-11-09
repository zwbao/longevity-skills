```bash
python "$SKILL/scripts/personal_report.py" --measurements body.csv --age 78 --sex 女 --out out
```

`body.csv`：

```
item,value,unit
体重,48,kg
握力,15.5,kg
```

OSTA 指数 = 0.2 ×（48 − 78）= −6.00，高风险，可能骨质疏松：是；握力 15.5 kg 低于女性切点 18 kg，可能肌少症：是；可能骨肌减少症：是。这是合成输入，论文没有印出个人算例。

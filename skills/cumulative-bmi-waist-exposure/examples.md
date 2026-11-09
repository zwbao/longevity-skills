```bash
python "$SKILL/scripts/personal_report.py" --measurements obesity.csv --sex female --age 80 --out out
```

`obesity.csv`：

```
item,value,unit
BMI 1,25.0,kg/m2
BMI 2,26.0,kg/m2
BMI 3,24.5,kg/m2
腰围1,88,cm
腰围2,90,cm
腰围3,86,cm
间隔1,3,年
间隔2,2,年
```

累积 BMI 暴露 (1+2)/2×3 + (2+0.5)/2×2 = 7.0 kg/m²×年，累积腰围暴露 (8+10)/2×3 + (10+6)/2×2 = 43.0 cm×年（女性 85 cm 切点：(3+5)/2×3 + (5+1)/2×2 = 18.0），最近一次 BMI 超重。这是合成输入，论文没有印出个人算例。

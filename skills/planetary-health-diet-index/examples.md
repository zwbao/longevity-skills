```bash
python "$SKILL/scripts/personal_report.py" --measurements diet.csv --sex female --age 68 --out out
```

`diet.csv`（每日平均摄入；第 13–15 项是占总能量的百分比）：

```
item,value,unit
全谷物,40,g/d
薯类,120,g/d
蔬菜,250,g/d
水果,150,g/d
奶类,300,g/d
红肉,60,g/d
禽肉,40,g/d
蛋类,50,g/d
鱼和贝类,30,g/d
坚果,10,g/d
杂豆,20,g/d
大豆和豆制品,30,g/d
不饱和植物油,12,%
饱和脂肪,9,%
添加糖,8,%
```

这是合成输入，论文没有印出个人算例。加 `--targets targets.csv`（同样格式的目标摄入）会在 `out/levers.json` 写出每项达到目标后 PHDI 的变化。

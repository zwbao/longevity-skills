---
name: autogaita-kinematics
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes personal knee and ankle angles, horizontal landmark velocities, and measured
  stride distance from a calibrated side-view walking cycle using AutoGaitA's published kinematic
  definitions. Use for personal gait coordinate analysis or repeated measurements under matched
  conditions. Requires complete joint tracking, not a step count or an unprocessed video.
---

# AutoGaitA 个人步态运动学

接收本人一个完整步态周期的二维坐标，生成中文报告、`result.json`
和 25 箱的 `cycle.csv`。提供的周期从同一侧脚离地开始，到下一次该脚离地前
最后一帧结束；需包含完整摆动和支撑阶段。不是两只脚交替的半个周期。

```bash
python3 scripts/personal_report.py --measurements /path/to/my-cycle.csv --age 65 --sex female --out /path/to/out
```

年龄、性别可省略；只作为样本适用范围的上下文，不改变计算。
不提供 `--targets`：这是测量读出，没有可据以设定健康目标的风险方程。

## 输入与准备

- 表头严格为 `item,value,unit`，按时间顺序分帧。
- 每帧第一行是 `time_s`，随后写 `hip_x_cm`、`hip_y_cm`、`knee_x_cm`、
  `knee_y_cm`、`ankle_x_cm`、`ankle_y_cm`、`midfoot_x_cm`、`midfoot_y_cm`。
  下一行 `time_s` 开始下一帧。各项目也接受 `skill.json` 中的中英文别名。
- 时间以秒计，也接受毫秒；坐标以厘米计，也接受米、毫米。别名行须写单位。
- 用同一侧腿的侧面追踪：髋、膝、踝、足中部。坐标须经本人拍摄场景的尺度标定，
  x 正方向为行走前方，y 正方向向上。不能填像素、混用两侧、把脚趾当足中部，
  或用动物实验的像素换算系数。更详细的格式见 [input-format.md](references/input-format.md)。
- 仅支持地面向前行走、等间隔采样、完整且已核查的追踪数据。
  不接收跑步机、转身、倒走、缺帧、自动填补数据或单张照片。

由助手完成本人已有追踪表的格式转换。只有原始视频时，先说明需要经过姿态追踪、
尺度标定与人工周期标注，不把缺失坐标猜出来。不向用户索取论文、附录、
公开代码、MoVi 数据或群组参考表；这里的计算不需要下载这些材料。

## 解释输出

膝、踝输出三个标志点的内角，不是临床测角仪的中立位读数。
跨步距离按足中部最大横坐标减起点横坐标计算。
水平速度是每个标志点的 x 分量，已换成厘米/秒；峰值在 25 箱归一化曲线上取。
完整原始周期用于角度极值和跨步距离，不用归一化曲线替代这些极值。

不把这些数分为正常/异常，不给年龄、推进力、跌倒概率或同龄百分位。
重复测量必须保持设备、标定、步行速度条件、追踪方式和起止定义一致；
一次差值不能直接解释为衰老速度或干预效果。

缺项、错误单位、超范围、时间不等间隔、关节重合等使脚本退出 3，
并写 `out/problems.json`；助手据此告诉用户具体要补测或修正哪项。
成功时读取 `out/report.md` 与 `out/result.json`。错误报告同样先放论文卡片。

报告始终保留：

> 边界: 本报告描述已标注步态周期的二维运动学，不测量地面反作用力或肌力，不判断衰弱、跌倒风险或生物年龄，也不能据此调整药物。

方法范围、参数出处和未复现部分见 [contract.md](references/contract.md)，
全部附件审计见 [sources.md](references/sources.md)。

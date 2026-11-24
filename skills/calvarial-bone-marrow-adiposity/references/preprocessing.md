# 个人影像如何进入此方法

此技能的计算入口只接收作者提取程序产生的个人矩阵。0–255 是论文约定的 MRI 信号尺度，无物理脂肪单位；不能从体检表、DXA 数值、文字影像报告或截图构造该矩阵。

对已经有原始 T1 MRI 的人，agent 自行获取 [作者 v1.2](https://github.com/comgen/boneMarrowLocalisationT1wMRI/tree/v1.2) 的 `010_extractIntensities` 和 `000_README.pdf`，不把公开文件获取任务交给用户。按照原 README 配置 FreeSurfer 5.3.0、FSL 6.0.1、Matlab R2018a；这些软件不包含在本技能 Python 依赖中。本环境未运行或验证这段预处理。

先执行 FreeSurfer 标准 recon-all，保留个人 `nu.mgz` 和 `aseg.mgz`。作者 `mainscript.sh` 使用 mri_watershed 提取皮肤表面，`makeIndividualMask.m` 根据小脑和伏隔核界定颅顶，再用 mri_vol2surf 按 0.5 mm 向内逐层取值至 25 mm；`compileLayers.m` 导出 `*_layers.csv`，为分号分隔、无表头的 50×N 矩阵。脚本要求按本机实际环境修改路径，不能直接执行作者的集群路径。Matlab MRIread/MRIwrite 需使用 FreeSurfer 的对应函数。

仅使用正确归一化且按作者几何/掩膜定义提取的信号；不要用普通 NIfTI 体素展开表、任意解剖切片或每个扫描重新 min-max 到 255 的值代替。模型数学输入范围检查无法识别所有预处理来源错误。预处理成功后仍须核对区域和边界；后续 Python 质控未通过时不发布个人指标。

输入总位点必须足够；零化的掩膜外位点允许存在，由作者的强度和规则排除。其余位点不能缺层或填补缺值。

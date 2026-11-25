"""Watson et al., Nature 2026, Methods: High VAF variants in the UK Biobank.

Only the printed amino-acid substitutions are expanded. The paper's '27 genomic
positions' is not a count of protein codons or of expanded substitutions.
"""
SWEEP_VAF_FRACTION = 0.30
MIN_VARIANT_READS = 3
HOTSPOT_GROUPS = {
    'DNMT3A': ('R320*', 'R326C/G/S', 'R598*', 'R729G/W', 'Y735C/F', 'R736C/G/H/L/S', 'R771*', 'R882H/C/S/L/P', 'W860R', 'P904L/Q/R'),
    'GNB1': ('K57E',),
    'IDH1': ('R132H',),
    'IDH2': ('R140Q', 'R172K'),
    'JAK2': ('V617F',),
    'KIT': ('D816F/H/V/Y',),
    'KRAS': ('G12C/D/V',),
    'MPL': ('W515L',),
    'NRAS': ('G12C/D/V',),
    'SF3B1': ('K666N', 'K700E'),
    'SRSF2': ('P95H/L/R',),
}
HOTSPOTS = frozenset(
    f'{gene} p.{group.split("/")[0][:-1]}{change}'
    for gene, groups in HOTSPOT_GROUPS.items()
    for group in groups
    for change in [group.split('/')[0][-1], *group.split('/')[1:]]
)
# Engineering input bounds, NOT published clinical thresholds; see contract.md.
COUNT_RANGES = {'total_reads_count': (1, 1_000_000_000), 'variant_reads_count': (0, 1_000_000_000)}
BOUNDARY = '这是单条血液变异的论文筛查条件核对，不是白血病诊断或个人发病概率；高 VAF 不能单独证明体细胞来源，未命中不能排除其他克隆或未来白血病，也不能据此开始或停止药物。'
STATUS_ZH = {
    'meets_screen': '这条变异符合论文热点高 VAF 筛查条件；体细胞来源仍需独立核实。',
    'below_or_equal_cutoff': '这条热点变异未超过论文 VAF 切点；这不等于个人筛查阴性或没有风险。',
    'insufficient_support': '这条变异支持读段不足，按论文规则过滤，不能据此判定扫荡。',
    'outside_panel': '这条变异不在论文列出的热点替换名单内，不能套用本筛查规则。',
}

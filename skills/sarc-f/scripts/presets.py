"""Malmstrom et al., JCSM 2016; Methods: SARC-F questionnaire (0–10 points)."""
ITEM_KEYS = ('strength_score', 'walking_score', 'chair_score', 'stairs_score')
INPUT_UNITS = {key: '1' for key in (*ITEM_KEYS, 'falls_past_year_count', 'sex')}
INPUT_UNITS['age'] = 'a'
ITEM_MIN, ITEM_MAX = 0, 2
FALLS_HIGH_MIN = 4
FALLS_SOME_MIN = 1
POSITIVE_MIN = 4
TOTAL_MAX = 10
LABELS = {
    'strength_score': '提举或搬运10磅物品',
    'walking_score': '走过一个房间',
    'chair_score': '从椅子或床起身转移',
    'stairs_score': '爬一段10级台阶',
    'falls_score': '过去一年跌倒',
}
BOUNDARY = ('SARC-F是症状筛查，不能确诊或排除肌少症，也不预测个人死亡概率或寿命；'
            '不能据此开始、停止或调整药物。')

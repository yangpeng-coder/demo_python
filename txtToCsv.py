# import json
# 生データのファイル名
FROM_FILE = "testADB_touchMesocket1_log_2020.05.07.txt"
# 処理済ファイル名と列目
TO_FILE = 'result.txt'
VALUE_FROM = 71
VALUE_TO = 79
COLUMNS = [
    # {
    #     'name': '被験者番号',
    #     'bind_name': None,
    #     'from': None,
    #     'to': None,
    #     'value': 1,
    # },
    {
        'name': 'ミリ秒(n)',
        'bind_name': 'TIME',    # 固定
        'from': 1,
        'to': 16,
    },
    {
        'name': 'x軸(n)',
        'bind_name': 'ABS_MT_POSITION_X',
        'from': VALUE_FROM,
        'to': VALUE_TO,
    },
    {
        'name': 'y軸(n)',
        'bind_name': 'ABS_MT_POSITION_Y',
        'from': VALUE_FROM,
        'to': VALUE_TO,
    },
    {
        'name': '圧力(n)',
        'bind_name': 'ABS_MT_PRESSURE',
        'from': VALUE_FROM,
        'to': VALUE_TO,
    },
    # {
    #     'name': '面積(n)',
    #     'bind_name': 'ABS_MT_TOUCH_MAJOR',
    #     'from': VALUE_FROM,
    #     'to': VALUE_TO,
    # }
]

# 抽出したいデータの設備名
DEVICE_CODE = '/dev/input/event4'
# 生データに行の並び順番
KEYS = ('ABS_MT_TRACKING_ID', 'BTN_TOUCH', 'ABS_MT_POSITION_X', 'ABS_MT_POSITION_Y', 'ABS_MT_PRESSURE', 'SYN_REPORT')
KEY_FROM = 50
KEY_TO = 68
# イベントの項目名
EVENT_NAME = 'BTN_TOUCH'
# イベントの情報
EVENT_VALUE_FROM = 'DOWN'
EVENT_VALUE_TO = 'UP'
# 被験者ID
USER_ID = '1'


def parse_data():
    max = 0
    with open(FROM_FILE, 'r', encoding='utf-8') as f:
        data = f.readlines()

    result_data = []
    data_json = {'TIME': []}
    i = 0
    # データ補充
    for row in data:
        if row.find(DEVICE_CODE) != -1 and row.find('add device') == -1:
            data_json['TIME'].append(row[1: 16])
            action = row[KEY_FROM:KEY_TO]
            # 省略データがある場合
            while action.find(KEYS[i]) < 0 and i < len(KEYS):
                # 前回のデータを配列に入れる
                data_json[KEYS[i]].append(data_json[KEYS[i]][-1])
                i += 1

            if action.find(KEYS[i]) >= 0:
                if KEYS[i] in data_json:
                    data_json[KEYS[i]].append(row[VALUE_FROM:VALUE_TO])
                else:
                    data_json[KEYS[i]] = [row[VALUE_FROM:VALUE_TO]]
                i += 1

            if i == len(KEYS):
                i = 0
    # print(json.dumps(data_json, indent=4))

    tmp = 0
    event_count = len(data_json[EVENT_NAME])
    out_row_data = [USER_ID]
    for j in range(event_count):
        tmp += 1
        for col in COLUMNS:
            out_row_data.append(data_json[col['bind_name']][j])

        # イベントがUPの場合
        # print(out_row_data)
        if data_json[EVENT_NAME][j].find(EVENT_VALUE_TO) != -1:
            result_data.append(','.join(out_row_data) + '\n')
            out_row_data = [USER_ID]
            if tmp > max:
                max = tmp

            tmp = 0

    # ヘッダ作成
    print(max)
    heads = ['被験者番号']
    for k in range(max):
        for col in COLUMNS:
            heads.append(col['name'].replace('n', str(k + 1)))
            
    result_head = ','.join(heads) + '\n'

    with open(TO_FILE, 'a', encoding='utf-8') as f:
        # ヘッダ
        f.writelines(result_head)
        f.writelines(result_data)


if __name__ == '__main__':
    parse_data()

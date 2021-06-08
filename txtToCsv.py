#  Copyright (c) 2021. 楊鵬. All Rights Reserved.

from datetime import datetime
import sys
import getopt

# キーワード
KEYWORD_LIST = ['huawei', 'pixel4a']
# 処理ファイルに項目名のindex
KEY_FROM = 50
KEY_TO = 68
# タッチイベントの項目名
EVENT_NAME = 'BTN_TOUCH'
# イベントの情報
EVENT_VALUE_FROM = 'DOWN'
EVENT_VALUE_TO = 'UP'
# イベント終了項目名
EVENT_STOP_FLAG = 'SYN_REPORT'

# 抽出したいデータのindex
VALUE_FROM = 71
VALUE_TO = 79
# 被験者ID
USER_COLUMN_NAME = '被験者番号'
# ミリ秒値の位置
TIMESTAMP_FROM = 1
TIMESTAMP_TO = 16
# 出力列項目
COLUMNS = [
    {
        'name': USER_COLUMN_NAME,  # 固定
    },
    {
        'name': 'ミリ秒(n)',
        'bind_name': 'TIME',  # 固定
        'from': TIMESTAMP_FROM,
        'to': TIMESTAMP_TO,
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
    {
        'name': '面積(n)',
        'bind_name': 'ABS_MT_TOUCH_MAJOR',
        'from': VALUE_FROM,
        'to': VALUE_TO,
    }
]


def get_options(argv):
    input_file = ''
    output_file = ''
    device_code = ''
    user_id = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:o:d:u:', ['input_file=', 'output_file=', 'device_code=', 'user_id'])
        # パラメータが4個ではない場合、エラーを投げる
        if len(opts) != 4:
            raise Exception
    except Exception:
        print('test.py -i <inputfile> -o <outputfile> -d <device_code> -u <user_id>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-i', '--input_file'):
            input_file = arg
        elif opt in ('-o', '--output_file'):
            output_file = arg
        elif opt in ('-d', '--device_code'):
            device_code = arg
        elif opt in ('-u', '--user_id'):
            user_id = arg
    if input_file == '' or output_file == '' or device_code == '' or user_id == '':
        print('test.py -i <inputfile> -o <outputfile> -d <device_code> -u <user_id>')
        sys.exit()

    return [input_file, output_file, device_code, user_id]


# 処理ファイルから補充済データ、項目名を取得
def create_data_from_file(file_name, keyword, device_code):
    data_json = {'TIME': []}
    keys = []
    i = 0
    index = KEYWORD_LIST.index(keyword);

    if index == -1:
        print('can not found keyword from file name...')
        sys.exit()

    with open(file_name, 'r', encoding='utf-8') as f:
        for row in f.readlines():
            if row.find(device_code) > -1 and row.find('add device') == -1:
                key = str.strip(row[KEY_FROM:KEY_TO])
                # pixel4aの特別のデータを集めないように
                if index == 1:
                    if (key == 'ABS_MT_PRESSURE' and row[VALUE_FROM:VALUE_TO] == '00000000') or (
                            key == 'ABS_MT_TRACKING_ID' and row[VALUE_FROM:VALUE_TO] == 'ffffffff'):
                        continue
                data_json['TIME'].append(str.strip(row[TIMESTAMP_FROM:TIMESTAMP_TO]))
                # 生データに項目名及び順番を取得
                if not (key in keys):
                    keys.append(key)

                # 省略データがある場合
                while key.find(keys[i]) < 0 and i < len(keys):
                    # 前回のデータを配列に入れる
                    # UPイベントにx軸、y軸以外のデータを0になる
                    if (data_json[EVENT_NAME][-1].find(EVENT_VALUE_TO) > -1) and (
                            not keys[i] in ['ABS_MT_POSITION_X', 'ABS_MT_POSITION_Y']):
                        data_json[keys[i]].append('0')
                    else:
                        data_json[keys[i]].append(data_json[keys[i]][-1])
                    i += 1

                if key.find(keys[i]) > -1:
                    value = row[VALUE_FROM:VALUE_TO]
                    # 16進数 -> 10進数
                    if key != EVENT_NAME:
                        value = int(value, 16)

                    if keys[i] in data_json:
                        data_json[key].append(str(value))
                    else:
                        data_json[key] = [str(value)]
                    i += 1

                if i == len(keys) and key == EVENT_STOP_FLAG:
                    i = 0
    if len(keys) == 0:
        print('device_code:', device_code, 'is missed...')
        sys.exit()
    return [data_json, keys]


def get_keyword(file_name):
    for keyword in KEYWORD_LIST:
        if file_name.lower().find(keyword) == -1:
            continue
        else:
            return keyword
    return ''


# データ転置
def data_convert(data_json, keys, user_id):
    # 一行に最大イベント数
    max_event_count_in_row = 0
    event_count_in_row = 0
    event_count_all = len(data_json[EVENT_NAME])
    # 出力行データ
    result_data = []
    # 行データ
    row_data = []
    rows = []
    max_len = 0;
    for i in range(event_count_all):
        event_count_in_row += 1
        for col in COLUMNS:
            if col['name'] == USER_COLUMN_NAME and data_json[EVENT_NAME][i].find(EVENT_VALUE_TO) != -1:
                row_data.insert(0, user_id)
            elif col['name'] != USER_COLUMN_NAME and (col['bind_name'] in keys or col['bind_name'] == 'TIME'):
                row_data.append(data_json[col['bind_name']][i])
        # イベントがUPの場合
        if data_json[EVENT_NAME][i].find(EVENT_VALUE_TO) != -1:
            rows.append(row_data)
            if event_count_in_row > max_event_count_in_row:
                max_event_count_in_row = event_count_in_row
                max_len = len(row_data)
            # カウントをリセット
            event_count_in_row = 0
            # 行データをリセット
            row_data = []

    # result_dataの長さを統一する（0を埋め込む）
    for row in rows:
        if len(row) < max_len:
            row.extend(['0'] * (max_len - len(row)))
        result_data.append(','.join(row) + '\n')

    # 出力ヘッダを作成
    result_header = []
    header = []
    for j in range(max_event_count_in_row):
        for col in COLUMNS:
            if col['name'] == USER_COLUMN_NAME and j == 0:
                header.append(USER_COLUMN_NAME)
            elif col['name'] != USER_COLUMN_NAME and (col['bind_name'] in keys or col['bind_name'] == 'TIME'):
                header.append(col['name'].replace('n', str(j + 1)))
    result_header.append(','.join(header) + '\n')
    return result_header + result_data


def create_file_from_data(data, file_name):
    now = datetime.now()
    # ファイル名に最後の「.」で切り分け
    [name, extension] = file_name.rsplit('.', 1)
    output_file_name = name + now.strftime('%Y%m%d%H%M%S%f') + '.' + extension
    with open(output_file_name, 'w', encoding='utf-8') as f:
        f.writelines(data)


if __name__ == '__main__':
    # コマンドのオプションを取得
    [input_file, output_file, device_code, user_id] = get_options(sys.argv[1:])
    # キーワードを取得
    keyword = get_keyword(input_file)
    # 処理ファイルを読み込み
    [data_json, keys] = create_data_from_file(input_file, keyword, device_code)
    # データ処理、転置
    convert_data = data_convert(data_json, keys, user_id)
    # ファイルを出力
    create_file_from_data(convert_data, output_file)

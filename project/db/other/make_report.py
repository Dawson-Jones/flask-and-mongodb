import time
import requests
import json


def combine_list(li: list, *args) -> list:
    for ele in args:
        if isinstance(ele, (list, tuple)):
            li += ele
        else:
            li.append(ele)
    return li


def convert_coord(flag: bool, position: str, amount: int):
    """convert coordinate yc to mes

    flag: True -> el_no belong to ['1', '2', '3']
    position: coordinate string like "1 2" split with space
    amount: how many cells in whole panel

    return: a correct coordinate in mes
    """
    coord_x, coord_y = position.split()
    if flag:
        position = ' '.join([str(7 - int(coord_x)), coord_y])
    else:
        temp_num = amount / 6 + 1
        position = ' '.join([coord_x, str(temp_num - int(coord_y))])

    return position


def load_config():
    info_map = {
        'EL_CODE': {'cr': 'NG隐裂',
                    'mr': 'NG混档',
                    'bc': 'NG失效',
                    'cs': 'NG虚焊',
                    'br': 'NG破片',
                    'bb': 'NG断栅',
                    'Black_Edge_shadow': 'NG黑边',
                    'other': 'NG其他'},
        'VI_CODE': {'spacing between cell or string NG': '串_片间距',
                    'Membrane migration': '膜偏',
                    'string dislocation': '错位',
                    'foreign matter': '异物',
                    'VI broken cell': '外观破片',
                    'barcode NG': '条码贴反',
                    'Ribbon excess': '焊带未剪',
                    'VI others': '外观其他',
                    'Ribbon migration': '焊带偏移',
                    'color difference': '色差',
                    'creepage distance': '隔离不到位'}
    }

    return info_map


def make_report(res):
    csv_data = [
        [
            '组件条码', '组件拍摄时间', '拍摄时间范围', 'AI 判定结果', 'EL 判定结果', '外观判定结果', '扫码机台',
            '组件测试次数', 'mes 结果', '层叠线信息', '不良原因', '不良位置', '人工删减', '单一电池隐裂数'
        ]
    ]
    info_map = load_config()

    for data in res:
        filed = list()
        if (not data.get('barcode')) or data['barcode'] == '0':
            continue
        filed.append(data['barcode'])
        local_time = time.localtime(data['create_time'])
        filed.append(time.strftime("%Y-%m-%d %H:%M:%S", local_time))
        y_m_d = time.strftime("%Y-%m-%d", local_time)
        hour = local_time.tm_hour
        if hour % 2 == 1:
            filed.append('%s %02d:00-%d:00' % (y_m_d, hour - 1, hour + 1))
        else:
            filed.append('%s %02d:00-%d:00' % (y_m_d, hour, hour + 2))
        judge_res = data['status']
        for i in judge_res:
            if i['by'] == 'AI':
                filed.append(i['result'])
                assert len(filed) == 4
            if i['by'] == 'OP':
                filed.append(i['result'])
                assert len(filed) == 5
        filed.append(data.get('ap_result') if data.get('ap_result') else 'N/A')  # ap 判定结果
        el_no = data['el_no']
        filed.append(el_no)  # 扫码机台
        filed.append(data['times_of_storage'])  # 组件测试次数
        filed.append(data.get('mes_res') if data.get('mes_res') else '暂无')
        filed.append(data.get('stack_equipment') if data.get('stack_equipment') else '暂无')

        # --------------------------------------------------> 不变

        el_no_series = el_no[-1]
        cell_amount = data['cell_amount']
        flag = True if el_no_series in ['1', '2', '3'] else False
        filed_res = filed[:]
        # 不良原因 和 不良位置
        many_cracks = dict()
        many_cracks_op = dict()
        ai_position = list()
        if not data['defects']:
            li = combine_list(filed, 'N/A', 'N/A', 'N/A', 'N/A')
            csv_data.append(li)
            continue

        for defect in data['defects']:
            if defect['by'] == 'AI':
                ai_position.append(defect['position']['c'])
        for defect in data['defects']:
            if defect["by"] == 'OP' and defect['position']['c'] not in ai_position:
                form = defect['type']
                form = info_map['EL_CODE'][form]
                position = defect['position']["c"]
                key = f'{form}#{position}'
                if not many_cracks_op.get(key):
                    many_cracks_op[key] = 0
                many_cracks_op[key] += 1

            if defect['by'] != 'AI':
                continue
            form = defect['type']
            form = info_map['EL_CODE'][form]
            position = defect['position']["c"]
            position = convert_coord(flag, position, cell_amount)
            deleted = 'Y' if defect["status"] == 'true' else 'N'
            key = f'{form}#{position}#{deleted}'
            if not many_cracks.get(key):
                many_cracks[key] = 0
            many_cracks[key] += 1

        for key, value in many_cracks.items():
            char_li = key.split('#')
            if char_li[0] == 'NG隐裂':
                char_li.append(value)
            else:
                char_li.append('N/A')
            filed_temp = filed[:]
            filed_temp += char_li
            csv_data.append(filed_temp)

        for key, value in many_cracks_op.items():
            char_li = key.split('#')
            if char_li[0] == 'NG隐裂':
                char_li.append('N/A')
                char_li.append(value)
            else:
                char_li.append('N/A')
                char_li.append('N/A')
            filed_temp = filed[:]
            filed_temp += char_li
            csv_data.append(filed_temp)

        # appearance defect
        if data.get('ap_defects'):
            for key, values in data['ap_defects'].items():
                if values:
                    for value in values:
                        filed_temp = filed_res[:]
                        li = combine_list(filed_temp, info_map["VI_CODE"][key], value, 'N/A', 'N/A')
                        csv_data.append(li)

    return csv_data



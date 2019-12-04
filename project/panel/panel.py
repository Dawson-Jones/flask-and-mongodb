import time
import csv
import random
from . import api
from project import db
from flask import request, jsonify, current_app
from log_manager import logger
from project.utils.response_code import RET

collection = db['panel']


@api.route('/')
def index():
    return 'hello, world'


@api.route('/gen_csv')
def gen_csv():
    hours = request.args.get('hours', '4')
    try:
        hours = int(hours)
    except Exception as e:
        logger.error(e)
        return jsonify(resno=RET.PARAMERR, msg='param must be a integer')

    # csv_data = [
    #     ["组件条码", "机台号", "判定用时", "返工组件？", "结果上传时间",
    #      "AI判定结果", "复核后结果", "外观判定结果(OK / NG)", "综合结果(OK/NG)", "STATUS"],
    # ]
    csv_data = [
        ["组件条码", "机台号", "判定用时", "返工组件？", "结果上传时间",
         "AI判定结果", "复核后结果", "外观判定结果(OK / NG)", "综合结果(OK/NG)"],
    ]
    timestamp = time.time()
    res = collection.find({"create_time": {"$gt": time.time() - hours * 3600}}).sort('create_time', -1)
    if not res.count():
        return jsonify(resno=RET.NODATA, msg='there is no matching data')

    flag = True
    for i in res:
        filed = list()
        if not i.get('barcode'):
            continue
        filed.append(i['barcode'])  # 条码
        filed.append(i['el_no'] if i.get('el_no') else '')  # 机台号
        filed.append(i['judgement_time'] if i.get('judgement_time') else '')  # 判定用时
        filed.append('是' if int(i.get('repaired')) else '否')  # 返工组件
        filed.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['create_time'])) if i.get(
            'create_time') else '')  # 结果上传时间

        el_ai_result = i['status']['EL_AI']
        el_op_result = i['status']['EL_OP']
        ap_op_result = i['status']['AP_OP']
        filed.append(el_ai_result)
        filed.append(el_op_result)
        filed.append(ap_op_result)
        filed.append('OK' if el_op_result == 'OK' and ap_op_result == 'OK' else 'NG')

        """
            if el_ai_result == 'OK':
                if el_op_result == 'NG':
                    filed.append('Miss')
                else:
                    filed.append('OK')
            elif el_ai_result == 'NG':
                if el_op_result == 'OK':
                    filed.append('OverKill')
                else:
                    filed.append('NG')
        """
        csv_data.append(filed)

        if flag:
            timestamp = i['create_time']
            flag = False

    # file_header = ["组件条码", "机台号", "判定用时", "返工组件？", "结果上传时间", "综合结果(OK/NG)",
    #                "EL判定结果(OK / NG)", "AI判定结果", "复核后结果", "EL判定不良类型1", "EL判定不良1位置",
    #                "EL判定不良类型2", "EL判定不良2位置", "EL判定不良类型3", "EL判定不良3位置",
    #                "EL判定不良类型4", "EL判定不良4位置", "EL判定不良类型5", "EL判定不良5位置",
    #                "外观判定结果(OK / NG)",
    #                "外观判定不良类型1", "外观判定不良1位置", "外观判定不良类型2", "外观判定不良2位置",
    #                "外观判定不良类型3", "外观判定不良3位置", "外观判定不良类型4", "外观判定不良4位置",
    #                "外观判定不良类型5", "外观判定不良5位置"]
    time_struct = time.localtime(timestamp)
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    with open(f'./generated_file/{time_str}.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # for row in csv_data:
        #     writer.writerow(row)
        writer.writerows(csv_data)

    return jsonify(resno=RET.OK, msg='generated')


@api.route('/barcode/find/<int:barcode>')
def barcode_find(barcode):
    result = collection.find_one({"barcode": barcode}, {"_id": 0})
    return jsonify(result)


@api.route('/add_panel_test')
def add_panel():
    data_list = list()
    for i in range(10):
        panel_data = {
            "mes_defects": {},
            "defects": [],
            "barcode": random.randint(0, 9999999),
            "cell_type": "mono",
            "origin_defects": {},
            "cell_shape": "half",
            "status": {
                "EL_AI": "OK" if random.randint(0, 1) else "NG",
                "EL_OP": "OK" if random.randint(0, 1) else "NG",
                "AP_OP": "OK" if random.randint(0, 1) else "NG"
            },
            "el_no": "1",
            "ap_defects": {},
            "cell_amount": 144,
            "create_time": time.time(),
            "display_mode": 1,
            "repaired": random.randint(0, 1),  # 自己加的
            'judgement_time': random.randint(1, 5)  # 自己加的
        }
        data_list.append(panel_data)
        time.sleep(random.randint(1, 3))

    result = collection.insert_many(data_list)
    print(result.inserted_ids)
    return jsonify(resno=RET.OK, msg='add success')

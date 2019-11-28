import time
import csv
from . import api
from project import db
from flask import jsonify

collection = db['panel']


@api.route('/')
def index():
    return 'hello, world'


@api.route('/gen_csv')
def gen_csv():
    flag = True
    timestamp = ''
    csv_data = [
        ["组件条码", "机台号", "判定用时", "返工组件？", "结果上传时间", "综合结果(OK/NG)",
         "AI判定结果", "复核后结果", "外观判定结果(OK / NG)"],

    ]
    res = collection.find({"create_time": {"$gt": time.time() - 4 * 3600}}).sort('create_time', -1)
    for i in res:
        filed = list()
        if not i.get('barcode'):
            continue
        filed.append(i['barcode'])  # 条码
        filed.append(i['el_no'] if i.get('el_no') else '')  # 机台号
        filed.append(i['create_time'] if i.get('create_time') else '')  # 判定用时
        filed.append('是' if int(i.get('repaired')) else '否')  # 返工组件
        filed.append(i['create_time'] if i.get('create_time') else '')

        overall_res = 'OK'
        ai_result = "OK"
        op_result = 'OK'
        for j in i['status']:
            if j['result'] == 'NG':
                if j['by'] == 'AI':
                    ai_result = 'NG'
                elif j['by'] == 'OP':
                    op_result = 'NG'
                overall_res = 'NG'
        # print('overall_res', overall_res)
        # print('ai_result', ai_result)
        # print('op_result', op_result)
        filed.append(overall_res)
        filed.append(ai_result)
        filed.append(op_result)
        filed.append(i['ap_result'] if i.get('ap_result') else '暂无结果')
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
    with open(f'./generated_file/{time_str}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # for row in csv_data:
        #     writer.writerow(row)
        writer.writerows(csv_data)

    return '生成完成'


@api.route('/barcode/find')
def barcode_find():
    result = collection.find_one({"barcode": '2252998'}, {"_id": 0})
    print(result)
    return jsonify(result)


@api.route('/add_panel_test')
def add_panel():
    import random
    data_list = list()
    for i in range(10):
        panel_data = {
            "mes_defects": {},
            "ap_result": "OK" if random.randint(0, 1) else "NG",
            "defects": [],
            "barcode": "%07d" % (random.randint(0, 9999999)),  # 组件条码
            "cell_type": "mono",
            "origin_defects": {},
            "cell_shape": "half",
            "status": [
                {"by": "AI", "result": "OK" if random.randint(0, 1) else "NG"},
                {"by": "OP", "result": "OK" if random.randint(0, 1) else "NG"}
            ],
            "el_no": "1",  # 机台号
            "ap_defects": {},
            "cell_amount": 144,
            "create_time": time.time(),
            "display_mode": 1,
            "repaired": random.randint(0, 1)  # 自己加的
        }
        data_list.append(panel_data)

    result = collection.insert_many(data_list)
    print(result.inserted_ids)
    return '添加成功'

from . import api
from flask import request, jsonify
from log_manager import logger
from project.utils.response_code import RET
from yoozen_db.yc_database import panel_collection
from yoozen_db.yc_database import YcDataBase
from .make_report import make_report

yc_db = YcDataBase()


# @api.route('/gen_csv')
# def gen_csv():
#     # http://host:port/gen_csv?hours=5
#     hours = request.args.get('hours', '4')
#     try:
#         hours = int(hours)
#     except Exception as e:
#         logger.error(e)
#         return jsonify(errno=RET.PARAMERR, msg='param must be a integer')
#
#     csv_data = [
#         ["组件条码", "机台号", "判定用时", "返工组件？", "结果上传时间",
#          "AI判定结果", "复核后结果", "外观判定结果(OK / NG)", "综合结果(OK/NG)"],
#     ]
#     timestamp = time.time()
#     res = panel_collection.find({"create_time": {"$gt": time.time() - hours * 3600}}).sort('create_time', -1)
#     if not res.count():
#         return jsonify(errno=RET.NODATA, msg='there is no matching data')
#
#     flag = True
#     for i in res:
#         filed = list()
#         if not i.get('barcode'):
#             continue
#         filed.append(i['barcode'])  # 条码
#         filed.append(i['el_no'] if i.get('el_no') else '')  # 机台号
#         filed.append(i['judgement_time'] if i.get('judgement_time') else '')  # 判定用时
#         filed.append('是' if int(i.get('repaired')) else '否')  # 返工组件
#         filed.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['create_time'])) if i.get(
#             'create_time') else '')  # 结果上传时间
#
#         el_ai_result = i['status']['EL_AI']
#         el_op_result = i['status']['EL_OP']
#         ap_op_result = i['status']['AP_OP']
#         filed.append(el_ai_result)
#         filed.append(el_op_result)
#         filed.append(ap_op_result)
#         filed.append('OK' if el_op_result == 'OK' and ap_op_result == 'OK' else 'NG')
#
#         """
#             if el_ai_result == 'OK':
#                 if el_op_result == 'NG':
#                     filed.append('Miss')
#                 else:
#                     filed.append('OK')
#             elif el_ai_result == 'NG':
#                 if el_op_result == 'OK':
#                     filed.append('OverKill')
#                 else:
#                     filed.append('NG')
#         """
#         csv_data.append(filed)
#
#         if flag:
#             timestamp = i['create_time']
#             flag = False
#
#     time_struct = time.localtime(timestamp)
#     time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
#     with open(f'./generated_file/{time_str}.csv', 'w', newline='', encoding='utf-8-sig') as f:
#         writer = csv.writer(f)
#         # for row in csv_data:
#         #     writer.writerow(row)
#         writer.writerows(csv_data)
#
#     return jsonify(errno=RET.OK, msg='generated')


# @api.route('/add_panel_test')
# def add_panell():
#     # 函数不能重名
#     data_list = list()
#     for i in range(10):
#         panel_data = {
#             "mes_defects": {},
#             "defects": [],
#             "barcode": random.randint(0, 9999999),
#             "cell_type": "mono",
#             "origin_defects": {},
#             "cell_shape": "half",
#             "status": {
#                 "EL_AI": ["OK", "NG"][random.randint(0, 1)],
#                 "EL_OP": ["OK", "NG"][random.randint(0, 1)],
#                 "AP_OP": ["OK", "NG"][random.randint(0, 1)]
#             },
#             "el_no": "1",
#             "ap_defects": {},
#             "cell_amount": 144,
#             "create_time": time.time(),
#             "display_mode": 1,
#             "repaired": random.randint(0, 1),  # 自己加的
#             'judgement_time': random.randint(1, 5)  # 自己加的
#         }
#         data_list.append(panel_data)
#
#     result = panel_collection.insert_many(data_list)
#     if result.inserted_ids:
#         return jsonify(errno=RET.OK, msg='add success')


@api.route('/repair', methods=['POST'])
def repair():
    data = request.get_json()
    yc_db.repair(data)


@api.route('/report')
def gen_report():
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    context = dict()
    if start_time:
        try:
            start_time = float(start_time)
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.PARAMERR, msg='time type error')
        context['create_time'] = dict()
        context['create_time']['$gt'] = start_time
    if end_time:
        try:
            end_time = float(end_time)
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.PARAMERR, msg='time type error')
        if context.get('create_time') is None:
            context['create_time'] = dict()
        context['create_time']['$lte'] = end_time
    if start_time and end_time:
        try:
            assert start_time <= end_time
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.PARAMERR, msg='date params wrong')
    res = panel_collection.find(context, {
        '_id': 0,
        'barcode': 1,
        'create_time': 1,
        'status': 1,
        'ap_result': 1,
        'el_no': 1,
        'mes_res': 1,
        'stack_equipment': 1,
        'cell_amount': 1,
        'defects': 1,
        'ap_defects': 1
    })
    # res.sort('create_time', -1)
    if not res:
        return jsonify(errno=RET.NODATA, msg='there is no matching data')

    res_li = make_report(res)
    return jsonify(errno=RET.OK, msg=res_li)

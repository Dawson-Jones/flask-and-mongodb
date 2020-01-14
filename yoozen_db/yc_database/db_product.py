import time
import json

from log_manager import logger
from ..utils.const_def import (
    CELL_AMOUNT_COLLECTION, CELL_SHAPE_COLLECTION, CELL_TYPE_COLLECTION, AI_RESULT,
    DEFECT_TYPE_COLLECTION, GUI_RESULT, PANEL_LIMIT
)


class Product(object):
    def __init__(self,
                 panel_collection, el_string_collection,
                 *args, **kwargs):
        self.panel_collection = panel_collection
        self.el_string_collection = el_string_collection

    def __limit(self, amount, create_time):
        t = time.localtime(time.time())
        time1 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', t), '%Y-%m-%d %H:%M:%S'))
        time2 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 23:59:59', t), '%Y-%m-%d %H:%M:%S'))
        # data = self.panel_collection.find({create_time: {'$gte': time1, '$lt': time2}}).count()
        data = self.panel_collection.count_documents({create_time: {'$gte': time1, '$lt': time2}})
        if data >= amount:
            return False
        else:
            return True

    def panel_add(self, info):
        barcode = info.get('barcode')
        create_time = info.get('create_time')
        el_no = info.get('el_no')
        mes_defects = info.get('mes_defects')
        cell_type = info.get('cell_type')
        cell_shape = info.get('cell_shape')
        cell_amount = info.get('cell_amount')
        display_mode = info.get('display_mode')
        ai_result = info.get('ai_result')
        ai_defects = info.get('ai_defects')
        gui_result = info.get('gui_result')
        ap_result = info.get('ap_result')
        ap_defects = info.get('ap_defects')
        gui_defects = info.get('gui_defects')
        origin_defects = info.get('origin_defects')
        if not all([
            barcode, create_time, el_no, mes_defects, cell_type, cell_shape,
            cell_amount, display_mode, ai_result, gui_result, ap_result
        ]):
            logger.error('incomplete params')
            return 'incomplete params', 400

        if not isinstance(mes_defects, str):
            logger.error('mes_defects should be dict')
            return 'mes_defects should be dict', 411
        if not isinstance(barcode, str):
            logger.error('barcode should be str')
            return 'barcode should be str', 411
        if cell_type not in CELL_TYPE_COLLECTION:
            logger.error('cell_type wrong')
            return 'cell_type wrong', 412
        if cell_shape not in CELL_SHAPE_COLLECTION:
            logger.error('cell_shape wrong')
            return 'cell_shape wrong', 412
        if cell_amount not in [60, 72, 120, 144, 156]:
            logger.error('cell_amount wrong')
            return 'cell_amount wrong', 412
        if not isinstance(el_no, str):
            logger.error('el_no should be str')
            return 'el_no should be str', 411
        if not isinstance(create_time, float):
            logger.error('create_time should be float')
            return 'create_time should be float', 411
        if display_mode not in [0, 1, 2]:
            logger.error('display_mode should be 0 or 1 or 2')
            return 'display_mode should be 0 or 1 or 2', 412
        if ai_result not in AI_RESULT:
            logger.error('ai_result should be %s' % (','.join(AI_RESULT)))
            return 'ai_result should be %s' % (','.join(AI_RESULT)), 412
        if ai_defects:
            if not isinstance(ai_defects, dict):
                logger.error('ai_defects should be dict')
                return 'ai_defects should be dict', 411
            for k in ai_defects.keys():
                if k not in DEFECT_TYPE_COLLECTION:
                    logger.error('ai_defects wrong')
                    return 'ai_defects wrong', 412
        if gui_result not in GUI_RESULT:
            logger.error('gui_result should be %s' % (','.join(GUI_RESULT)))
            return 'gui_result should be %s' % (','.join(GUI_RESULT)), 412
        if gui_defects:
            if not isinstance(gui_defects, dict):
                logger.error('gui_defects should be dict')
                return 'gui_defects should be dict', 411
            for k in gui_defects.keys():
                if k not in DEFECT_TYPE_COLLECTION:
                    logger.error('gui_defects wrong')
                    return 'gui_defects wrong', 411
        if not origin_defects:
            origin_defects = dict()
        if ap_result not in AI_RESULT:
            logger.error('ap_result should be %s' % (','.join(AI_RESULT)))
            return 'ap_result should be %s' % (','.join(AI_RESULT)), 412
        if ap_defects:
            if not isinstance(ap_defects, dict):
                logger.error('ap_defects should be dict')
                return 'ap_defects should be dict', 411
            for k in ap_defects.keys():
                if k not in DEFECT_TYPE_COLLECTION:
                    logger.error('ap_defects wrong')
                    return 'ap_defects wrong', 412

        defects = list()
        status = dict()
        status['EL_AI'] = ai_result
        status['EL_OP'] = gui_result
        status['AP_OP'] = ap_result
        if ai_defects:
            if not gui_defects:
                for key, values in ai_defects.items():
                    for value in values:
                        defects.append({'type': key, 'position': value, 'by': 'AI', 'status': 'true'})
            else:
                for key, values, in ai_defects.items():
                    for value in values:
                        gui_defects_list = gui_defects.get(key)
                        if gui_defects_list and (value in gui_defects_list):
                            defects.append({'type': key, 'position': value, 'by': 'AI', 'status': 'true'})
                            defects.append({'type': key, 'position': value, 'by': 'OP', 'status': 'true'})
                            gui_defects_list.remove(value)
                        else:
                            defects.append({'type': key, 'position': value, 'by': 'AI', 'status': 'false'})

        if gui_defects:
            for key, values in gui_defects.items():
                for value in values:
                    defects.append({'type': key, 'position': value, 'by': 'OP', 'status': 'true'})

        panel_check = self.panel_collection.find_one(
            {"barcode": barcode, "create_time": create_time, "el_no": el_no})
        if self.__limit(PANEL_LIMIT, 'create_time'):
            if panel_check:
                self.panel_collection.replace_one(panel_check, {
                    'barcode': barcode,
                    'cell_type': cell_type,
                    'cell_amount': cell_amount,
                    'cell_shape': cell_shape,
                    'display_mode': display_mode,
                    'el_no': el_no,
                    'create_time': create_time,
                    'origin_defects': origin_defects,
                    'defects': defects,
                    'status': status
                })
            else:
                self.panel_collection.insert_one({
                    'barcode': barcode,
                    'cell_type': cell_type,
                    'cell_amount': cell_amount,
                    'cell_shape': cell_shape,
                    'display_mode': display_mode,
                    'el_no': el_no,
                    'create_time': create_time,
                    'origin_defects': origin_defects,
                    'defects': defects,
                    'status': status,
                    "mes_defects": mes_defects,
                    "ap_defects": ap_defects
                })
        else:
            logger.error('panel limited')
            return "too much panels", 400
        logger.info('add panel')
        return '1', 200

    def string_add(self, info):
        image_id = info.get('image_id')
        create_time = info.get('create_time')
        string_line = info.get('string_line')
        cell_type = info.get('cell_type')
        cell_shape = info.get('cell_shape')
        cell_amount = info.get('cell_amount')
        result = info.get('result')
        defects = info.get('defects')
        insert_time = time.time()

        if not all([image_id, cell_type, cell_shape, cell_amount, string_line]):
            logger.error('incomplete params')
            return 'incomplete params', 400

        if not isinstance(image_id, str):
            logger.error('image_id should be str')
            return 'image_id should be str', 411
        if cell_type not in CELL_TYPE_COLLECTION:
            logger.error('cell_type wrong')
            return 'cell_type wrong', 412
        if cell_shape not in CELL_SHAPE_COLLECTION:
            logger.error('cell_shape wrong')
            return 'cell_shape wrong', 412
        if cell_amount not in CELL_AMOUNT_COLLECTION:
            logger.error('cell_amount wrong')
            return 'cell_amount wrong', 412
        if not isinstance(string_line, str):
            logger.error('string_line should be str')
            return 'string_line should be str', 411
        if defects:
            if not isinstance(defects, dict):
                logger.error('defects should be dict')
                return 'defects should be dict', 411
            for key in defects.keys():
                if key not in DEFECT_TYPE_COLLECTION:
                    logger.error('defects wrong')
                    return 'defects wrong', 412

        if self.__limit(PANEL_LIMIT, 'insert_time'):
            self.el_string_collection.replace_one(
                {
                    "image_id": image_id,
                    "create_time": create_time,
                    "string_line": string_line
                }, {
                    'image_id': image_id,
                    'result': result,
                    'cell_type': cell_type,
                    'cell_amount': cell_amount,
                    'cell_shape': cell_shape,
                    'string_line': string_line,
                    'create_time': create_time,
                    'defects': defects,
                    'insert_time': insert_time,
                }, True)
        else:
            logger.error('panel limited')
            return "too much panels", 400

    def barcode_find(self, info):
        barcode = info.get('barcode')
        if not barcode:
            logger.error('incomplete params')
            return 'incomplete params', 421
        res = self.panel_collection.find_one({'barcode': barcode}, {'_id': 0, 'thresholds': 0})
        return res, 200

    def panel_check_last(self, info):
        barcode = info.get('barcode')
        create_time = info.get('create_time')
        if not all([barcode, create_time]):
            logger.error('incomplete params')
            return 'incomplete params', 421
        res = self.panel_collection.find_one({'barcode': barcode, 'create_time': create_time})
        return '1' if res else '0'

    def repair(self, info):
        barcode = info.get('barcode')
        if not barcode:
            logger.error('incomplete params')
            return 'incomplete params', 421
        res = list(self.panel_collection.aggregate([
            {'$match': {"barcode": barcode}},
            {'$sort': {'create_time': -1}},
            {'$project': {'_id': 0, 'defects': '$mes_defects'}},
            {'$limit': 1}]))[0]
        return json.dumps(res), 200 if res else '0', 400

    def mes_defects_update(self, info):
        barcode = info.get('barcode')
        create_time = info.get('create_time')
        mes_defects = info.get('mes_defects')
        if not all([barcode, create_time, mes_defects]):
            logger.error('incomplete params')
            return 'incomplete params', 421
        panel_check = self.panel_collection.find_one({'barcode': barcode, 'create_time': create_time})
        if not panel_check:
            return 'no such panel', 422
        panel_check['mes_defects'] = mes_defects
        self.panel_collection.replace_one({'barcode': barcode, 'create_time': create_time}, panel_check)
        logger.info("mes_defects_update{%s}" % barcode)
        return '1', 200

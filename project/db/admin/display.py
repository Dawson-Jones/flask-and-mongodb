from flask import request, jsonify
from . import app
from yoozen_db.basic.db import *
from log_manager import logger
from project.utils.response_code import RET


# GET /admin/log?
@app.route('log')
def log():
    start_time = request.args.get('timeStart', '')
    end_time = request.args.get('timeEnd', '')
    el_no = request.args.get('el_no', '')
    page = request.args.get('page', 1)
    size = request.args.get('size', 10)

    context = dict()
    '''
    {
        'time': {
            '$gt': 3213,
            '$lte': 2344
        },
        '$or': [
            {'el_no': 'prea1'},
            {'el_no': 'prea2'}
        ]
    }
    '''
    if start_time:
        try:
            start_time = float(start_time)
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.DATAERR, msg='time type wrong')
        context['time'] = dict()
        context['time']['$gt'] = start_time
    if end_time:
        try:
            end_time = float(end_time)
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.DATAERR, msg='time type wrong')
        if context.get('time') is None:
            context['time'] = dict()
        context['time']['$lte'] = end_time
    if start_time and end_time:
        try:
            assert start_time <= end_time
        except Exception as e:
            logger.error(e)
            return jsonify(errno=RET.PARAMERR, msg='date params wrong')
    if el_no:
        el_no_li = el_no.split()
        mult_el = [{'el_no': i} for i in el_no_li]
        context['$or'] = mult_el

    try:
        page = int(page)
        size = int(size)
        if page < 0 or size < 0:
            return jsonify(errno=RET.PARAMERR, msg='page or size must be a unsigned integer')
    except Exception as e:
        logger.error(e)
        return jsonify(errno=RET.PARAMERR, msg='page or size must be a integer')

    res = user_log_collection.find(
        context, {'_id': 0, 'id': 0}).limit(size).skip((page - 1) * size)
    amount = user_log_collection.count_documents(context)
    pages = amount // size + 1
    if not amount:
        return jsonify(errno=RET.NODATA, msg='no data')
    li = list()
    for i in res:
        if not i.get('changed_before'):
            i['changed_before'] = {}
        if not i.get('changed_after'):
            i['changed_after'] = {}
        if i.get('changed_before').get('user_pw'):
            i['changed_before']['user_pw'] = '******'
            i['changed_after']['user_pw'] = '******'
        li.append(i)
    content = {
        'data': li,
        'pages': pages
    }
    return jsonify(errno=RET.OK, msg=content)

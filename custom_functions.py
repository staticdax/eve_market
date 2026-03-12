#!/usr/bin/env python3

import queue
import data_helper
import direct_api_functions
import multithread_functions
from datetime import datetime, timedelta
import json
import yaml
import csv
import requests


def get_item_market_history_of_region_from_api_or_local(region_id: int, type_id: int) -> list:
    if type_id in data_helper.market_history_dict[region_id]['history'].keys():
        if data_helper.market_history_dict[region_id]['history'][type_id]['updated']:
            # 直接从文件载入的updated都是都是False, 更新过API的数据就为True
            # print('data found in dict')
            return data_helper.market_history_dict[region_id]['history'][type_id]['data']
    else:
        data_helper.market_history_dict[region_id]['history'][type_id] = dict()
        data_helper.market_history_dict[region_id]['history'][type_id]['updated'] = False

    return direct_api_functions.get_item_market_history_of_region(region_id, type_id)


def get_last_n_day_volume(region_id: int, type_id: int, n: int) -> int:
    """
    得到最近N天的成交量

    :param region_id: 星域id
    :param type_id: 商品id
    :param n: 最近n天
    :return: 总成交量
    """
    volume_sum = 0
    trade_history_list = get_item_market_history_of_region_from_api_or_local(region_id, type_id)
    if len(trade_history_list) == 0:
        return volume_sum
    print(trade_history_list)
    minus_n_date = datetime.strptime(trade_history_list[-1]['date'], '%Y-%m-%d') - timedelta(n)
    check_pos_date = datetime.strptime(trade_history_list[-n]['date'], '%Y-%m-%d') if len(trade_history_list) > n \
        else datetime.strptime(trade_history_list[0]['date'], '%Y-%m-%d')
    time_delta = check_pos_date - minus_n_date
    if time_delta.days == 0:  # 最后n个记录和最后n天都一一对应
        trade_history_list = trade_history_list[-n:]
    elif time_delta.days < 0:  # 最后n个记录不和最后n天都一一对应，最后n天可能不是每天都有交易记录，最后n个记录可能是最后n+m天内的记录
        for i in range(1, n):  # 从后往前搜索，找到第一个不在最后n天范围内的记录，删除不需要的记录
            d = datetime.strptime(trade_history_list[-i]['date'], '%Y-%m-%d')
            time_delta = d - minus_n_date
            if time_delta.days < 0:
                trade_history_list = trade_history_list[-i + 1:]
                break

    print(trade_history_list)
    # print(type_id)
    for _ in trade_history_list:
        # print("{} _['volume']: {}".format(_['date'], _['volume']))
        volume_sum += _['volume']
    return volume_sum


def get_type_name(type_id: int):
    name = data_helper.get_type_name_from_dict(type_id)
    if name is None:
        info = direct_api_functions.get_type_id_info_from_api(type_id)
        if info is None:
            print('custom_functions.get_type_name() error, type_id: {}'.format(type_id))
            return
        else:
            data_helper.type_id_dict[type_id] = info['name']
            data_helper.typeid_packaged_volume_dict[type_id] = info['packaged_volume']
            return data_helper.type_id_dict[type_id]
    else:
        return name



def get_last_n_day_orders(region_id: int, type_id: int, n: int) -> int:
    """
    得到最近N天的成交量

    :param region_id: 星域id
    :param type_id: 商品id
    :param n: 最近n天
    :return: 总成交量
    """
    order_sum = 0
    trade_history_list = get_item_market_history_of_region_from_api_or_local(region_id, type_id)
    if len(trade_history_list) == 0:
        return order_sum
    # print(trade_history_list)
    minus_n_date = datetime.strptime(trade_history_list[-1]['date'], '%Y-%m-%d') - timedelta(n)
    check_pos_date = datetime.strptime(trade_history_list[-n]['date'], '%Y-%m-%d') if len(trade_history_list) > n \
        else datetime.strptime(trade_history_list[0]['date'], '%Y-%m-%d')
    time_delta = check_pos_date - minus_n_date
    if time_delta.days == 0:  # 最后n个记录和最后n天都一一对应
        trade_history_list = trade_history_list[-n:]
    elif time_delta.days < 0:  # 最后n个记录不和最后n天都一一对应，最后n天可能不是每天都有交易记录，最后n个记录可能是最后n+m天内的记录
        for i in range(1, n):  # 从后往前搜索，找到第一个不在最后n天范围内的记录，删除不需要的记录
            d = datetime.strptime(trade_history_list[-i]['date'], '%Y-%m-%d')
            time_delta = d - minus_n_date
            if time_delta.days < 0:
                trade_history_list = trade_history_list[-i + 1:]
                break

    # print(trade_history_list)
    # print(type_id)
    for _ in trade_history_list:
        # print("{} _['volume']: {}".format(_['date'], _['volume']))
        order_sum += _['order_count']
    return order_sum


def renew_region_markets_orders_dict_multi(thread_num=10, region='All'):
    """
    获得全部星域市场的订单，更新data_helper.market_orders_dict

    执行流程:
        ① 初始化: 清空 region_markets_orders_dict
        ② 确定范围: 根据 region 参数选择星域列表
        ③ 创建任务: MyGetTask 管理任务队列和结果
        ④ 启动线程: MyGetOrdersOfAllRegionsThread 并行获取订单
        ⑤ 收集结果: 将 result_dict 复制到 region_markets_orders_dict

    数据流:
        region_list → MyGetTask → MyGetOrdersOfAllRegionsThread × N → result_dict → region_markets_orders_dict

    内存注意:
        - result_dict 和 region_markets_orders_dict 存储相同数据
        - 峰值时内存翻倍，后续可优化直接写入目标字典

    :param region: 是否选择全星域，默认为是，否为帝国控制星域
    :param thread_num: 线程数
    :return: 无返回值，更新data_helper.region_markets_orders_dict {region_id_1:[{order_1},...], region_id_2:[{},...], ...}
    """
    data_helper.region_markets_orders_dict = dict()  # 清空旧数据，旧数据将由GC回收
    if region == 'All':
        region_list = data_helper.region_id_dict.keys()
    elif region == 'Empire regions':
        region_list = data_helper.empire_region_id_list
    if len(data_helper.region_markets_orders_dict) > 0:  # 冗余代码: 上面已清空，此条件永远为False
        data_helper.region_markets_orders_dict = dict()  # 永远不会执行
    get_all_orders_task = multithread_functions.MyGetTask(region_list)
    threads = [
        multithread_functions.MyGetOrdersOfAllRegionsThread(get_all_orders_task)
        for _ in range(thread_num)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for region_id, order_list in get_all_orders_task.result_dict.items():
        if len(order_list) > 0:
            data_helper.region_markets_orders_dict[region_id] = order_list

    # del threads

    # renew_all_orders_by_typeid_dict()
    # renew_detailed_profitable_orders_dict()


def renew_all_orders_by_typeid_dict():
    """
    更新data_help.all_orders_by_typeid_dict，
    若data_helper.region_markets_orders_dict为空则加载缓存文件到region_markets_orders_dict，
    然后更新data_help.all_orders_by_typeid_dict

    :return: 更新data_helper.all_orders_by_typeid_dict {type_id_1:[{order_1}, {order_2}, ...], type_id_2:[{},{},...], ...}
    """
    if len(data_helper.region_markets_orders_dict) == 0:
        print("data_helper.market_order_dict is not ready, loading saved files.")
        data_helper.region_markets_orders_dict = data_helper.load_market_order_dict_from_json()

    data_helper.all_orders_by_typeid_dict = dict()

    for orders in data_helper.region_markets_orders_dict.values():
        for order in orders:
            if order['type_id'] not in data_helper.all_orders_by_typeid_dict.keys():
                data_helper.all_orders_by_typeid_dict[order['type_id']] = list()
            data_helper.all_orders_by_typeid_dict[order['type_id']].append(order)


def get_active_order_in_region_multi_todo(region_id: int, thread_num=20):
    """
    获得星域市场订单
    TODO: 直接获取get_orders_of_region_single_thread(region_id: int, order_type='all', page=1, type_id=-1), 无需指定typeid

    :param region_id: 星域ID
    :param thread_num: 线程数
    :return: 列表 [(type_id_1, [{order_1}, {order_2}, ...]), (type_id_2, [{}, ...]), ...] ,
    是字典{type_id_1:[{order_1}, {order_2}, ...], typer_id_2:...}按订单数排序的结果
    """
    # type_list_active_in_region = direct_market_api_functions.get_type_ids_have_active_order_in_region(region_id)
    # task = multithread_functions.MyGetTask(type_list_active_in_region, region_id)
    # threads = [multithread_functions.MyGetCurrentOrderInRegionThread(task, i) for i in range(thread_num)]
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()
    #
    # sorted_result_list = sorted(task.result_dict.items(), key=lambda x: len(x[1]), reverse=True)
    # return sorted_result_list
    print("TODO: 重写")


def get_profitable_orders(order_dict: dict, tax_rate=0.05):
    """
    返回所有星域市场范围内可以赚取价差的订单

    :param order_dict: {type_id_1:[{order}, {}, ...], typer_id_2:...}, 形式与get_active_order_in_region_multi()返回一致
    :param tax_rate: 销售税率
    :return: profitable_bns_orders_dict {type_id_1:{'buy':[{order_1},{order_2},...],'sell':[{order_1}, ...]}, type_id_2:...}
    """
    profitable_bns_orders_dict, so_list, bo_list = dict(), list(), list()
    # tmp = get_active_order_in_region_multi(region_id, thread_num)
    for type_id, orders in order_dict.items():
        for o in orders:
            if o['is_buy_order']:
                bo_list.append(o)
            else:
                so_list.append(o)
            bo_list.sort(key=lambda x: x['price'], reverse=True)
            so_list.sort(key=lambda x: x['price'], reverse=False)

            if len(bo_list) > 0 and len(so_list) > 0 and bo_list[0]['price'] * (1 - tax_rate) > so_list[0]['price']:
                profitable_bns_orders_dict[type_id] = {'buy': bo_list, 'sell': so_list}
        so_list, bo_list = list(), list()
    return profitable_bns_orders_dict


def get_detailed_profitable_orders_dict(profitable_bns_orders_dict: dict, tax_rate=0.05, profit_min=0):
    """
    获取各差价订单详细信息的字典，type_id为键，值为详细信息的字典

    :param profitable_bns_orders_dict: get_profitable_orders()得到的字典
    {type_id_1:{'buy':[{order_1},{order_2},...],'sell':[{order_1}, ...]}, type_id_2:...}
    :param tax_rate: 空间站销售税率
    :param profit_min: 最低利润
    :return: profitable_orders_dict {type_id_1:{info1:info, info2:info, ..., buy:[{order}, ...]}, sell:[{order}, ...]}
    """
    profitable_orders_dict = dict()
    for type_id, bns_orders in profitable_bns_orders_dict.items():
        # print("{} {}".format(type_id, data_helper.get_type_name_from_dict(type_id)))
        sell_q = queue.Queue()
        buy_q = queue.Queue()
        for k, v in bns_orders.items():
            if k == 'buy':
                for o in v:
                    buy_q.put(o)
            elif k == 'sell':
                for o in v:
                    sell_q.put(o)
        profit_sum, volume, sell_n, buy_n, cost = 0, 0, 0, 0, 0
        buy_list, sell_list = [], []
        buy_order, sell_order = dict(), dict()
        tmp_order = None
        while (not sell_q.empty() and not buy_q.empty()) or (sell_n != 0 or buy_n != 0):  # 订单队列不为空，或者
            if (sell_q.empty() and sell_n == 0) or (buy_q.empty() and buy_n == 0):
                break
            # profit_single = 0
            if buy_n == 0:
                buy_order = buy_q.get()
                buy_n = buy_order['volume_remain']
            if sell_n == 0:
                sell_order = sell_q.get()
                sell_n = sell_order['volume_remain']
            profit_single = buy_order['price'] * (1 - tax_rate) - sell_order['price']
            if profit_single < 0:
                # print("negative profit")
                break
            else:
                if sell_n > buy_n:
                    sell_n -= buy_n
                    profit_sum += profit_single * buy_n
                    volume += buy_n
                    cost += buy_n * sell_order['price']
                    buy_n = 0
                    buy_list.append(buy_order)
                    tmp_order = sell_order
                elif sell_n < buy_n:
                    buy_n -= sell_n
                    profit_sum += profit_single * sell_n
                    volume += sell_n
                    cost += sell_n * sell_order['price']
                    sell_n = 0
                    sell_list.append(sell_order)
                    tmp_order = buy_order
                else:
                    profit_sum += profit_single * sell_n
                    volume += sell_n
                    cost += sell_n * sell_order['price']
                    sell_n, buy_n = 0, 0
                    buy_list.append(buy_order)
                    sell_list.append(sell_order)
                    tmp_order = None
        if tmp_order is not None:
            # print("检查队列")
            if tmp_order['is_buy_order']:
                buy_list.append(tmp_order)
            else:
                sell_list.append(tmp_order)
        if profit_sum > profit_min:
            profitable_orders_dict[type_id] = {'type_name': get_type_name(type_id),
                                               'profit': profit_sum,
                                               'buy_order_num': len(buy_list),
                                               'sell_order_num': len(sell_list),
                                               'volume': volume,
                                               'cost': cost,
                                               'profit_rate': profit_sum / cost,
                                               'buy': buy_list,
                                               'sell': sell_list,
                                               'total_volume': data_helper.typeid_packaged_volume_dict[
                                                                   type_id] * volume,
                                               'rating': profit_sum / cost / (len(buy_list) + len(sell_list))}
    return profitable_orders_dict
    # pure_profit_sorted_list = sorted(profitable_orders_dict.items(), key=lambda x:x[1]['profit'], reverse=True)
    # pure_profit_sorted_list = sorted(profitable_orders_dict.items(),
    #                                  key=lambda x: x[1]['rating'], reverse=True)
    # return pure_profit_sorted_list


def renew_detailed_profitable_orders_dict(tax_rate=0.05, min_profit=0):  # interstellar_logistic
    """
    更新data_helper.all_profitable_orders_dict
    {type_id_1:{info1:info, info2:info, ..., buy:[{order}, ...], sell:[{order}, ...]}, type_id_2: {...}, ...}

    :param tax_rate: 销售税率
    :param min_profit: 最小利润
    :return:
    """
    profitable_bns_orders_dict = get_profitable_orders(data_helper.all_orders_by_typeid_dict)
    data_helper.detailed_profitable_orders_dict = get_detailed_profitable_orders_dict(profitable_bns_orders_dict,
                                                                                      tax_rate, min_profit)


def get_sorted_detailed_profitable_orders_dict(profitable_orders_dict: dict, min_profit=0, sorted_by='rating',
                                               reverse=True):
    """
    对profitable_orders_dict进行排序，过滤，

    :param profitable_orders_dict: data_helper.all_profitable_orders_dict 或 data_helper.region_profitable_orders_dict
        {type_id_1: {'type_name': info, 'profit': info, ..., 'buy': [{order}, ...], 'sell': [{order}, ...]}, type_id_2: {...}, ...}
    :param min_profit: 最小利润
    :param sorted_by: 排序依据，可选'profit', 'buy_order_num', 'sell_order_num', 'volume', 'cost', 'profit_rate', 'rating'
    :param reverse: 是否降序排序，默认为降序排序
    :return: 经过排序后的detailed_profitable_orders_dict字典
    """
    if sorted_by not in list(profitable_orders_dict.values())[0].keys():
        print("sorted_by key not exists. Try again.")
        return []
    tmp_list = sorted(profitable_orders_dict.items(), key=lambda x: x[1][sorted_by], reverse=reverse)
    r_dict = dict()
    for rec in tmp_list:
        if rec[1]['profit'] >= min_profit:
            r_dict[rec[0]] = rec[1]

    return r_dict


def write_market_order_dict_to_file_todo():
    """
    将data_helper.market_orders_dict写入到文件data/markets/all_region_orders.json，供后续读取

    :return:
    """
    # if len(data_helper.region_markets_orders_dict) > 0:
    #     for region_id in data_helper.region_markets_orders_dict.keys():
    #         if len(data_helper.region_markets_orders_dict[region_id]) > 0:
    #             # print(region_id)
    #             multithread_functions.write_json_into_file_multi_thread('data/markets/{}'.format(region_id),
    #                                                                     'order.json',
    #                                                                     data_helper.region_markets_orders_dict[
    #                                                                         region_id])
    if len(data_helper.region_markets_orders_dict) > 0:
        data_helper.write_json_into_file('data/markets', 'all_region_orders.json',
                                         data_helper.region_markets_orders_dict)
    else:
        print("data_helper.market_order_dict's length is zero.")


def renew_datafile_type_id_tq_json():
    data_source = 'https://www.fuzzwork.co.uk/dump/latest'
    try:
        f = requests.get(data_source+'/invTypes.csv')
        with open('./data/invTypes.csv', 'wb') as fh:
            fh.write(f.content)
    except Exception as e:
        print("{} An error oucurred during download.".format(e))

    typedict = dict()
    with open('./data/invTypes.csv', 'r', encoding='utf-8') as fh:
        content = csv.DictReader(fh)
        for i in content:
            typeid = i['typeID']
            typedict[typeid] = i['typeName']

    with open('./data/type_id_tq.json', 'w', encoding='utf-8') as fh:
        json.dump(typedict, fh, indent=2)


def renew_datafile_type_id_n_typeid_volume_json_from_sde():
    typeid_source_file_name = 'typeIDs.yaml'
    typeid_file_name = 'type_id.json'
    typeid_volume_file_name = 'typeid_volume.json'
    with open('../eve_db/'+typeid_source_file_name, 'r', encoding='utf-8') as fh:
        y1 = yaml.safe_load(fh.read())

    typeid_name_dict = dict()
    typeid_volume_dict = dict()
    for i in y1.keys():
        if y1[i]['name'].__contains__('zh'):
            typeid_name_dict[str(i)] = y1[i]['name']['zh']
        else:
            typeid_name_dict[str(i)] = 'UNKNOWN'
    for i in y1.keys():
        if y1[i].__contains__('volume'):
            typeid_volume_dict[str(i)] = y1[i]['volume']

    with open('./data/'+typeid_file_name, 'w', encoding='utf-8') as fh:
        json.dump(typeid_name_dict, fh, indent=2)
    with open('./data/'+typeid_volume_file_name, 'w', encoding='utf-8') as fh:
        json.dump(typeid_name_dict, fh, indent=2)


def renew_datafile_typeid_packaged_volume_json_from_esi():
    with open('./data/typeid_packaged_volume.json.bak', 'r') as fh:
        typeid_pvol_dict = json.load(fh)

    for i in typeid_pvol_dict.keys():
        tmp = direct_api_functions.get_type_id_info_from_api(int(i))
        typeid_pvol_dict[i] = tmp['packaged_volume']

    with open('./data/typeid_packaged_volume,json', 'w') as fh:
        json.dump(typeid_pvol_dict, fh, indent=2)


def renew_datafile_typeid_packaged_volume_json():
    typeid_packaged_volume_dict = dict()
    with open('./data/typeid_packaged_volume_bak.json', 'r') as fh:
        typeid_packaged_volume_dict = json.load(fh)

    for i in typeid_packaged_volume_dict.keys():
        tmp = direct_api_functions.get_type_id_info_from_api(int(i))
        typeid_packaged_volume_dict[i] = tmp['packaged_volume']

    with open('./data/typeid_packaged_volume,json', 'w') as fh:
        json.dump(typeid_packaged_volume_dict, fh, indent=2)


if __name__ == '__main__':
    # ############## test get_type_name() ##############
    # print(get_type_name(55822))
    pass

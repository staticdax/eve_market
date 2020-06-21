#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-
import queue

import direct_market_api_functions
import data_helper
import multithread_functions
from datetime import datetime, timedelta


def get_item_market_history_of_region_from_api_or_local(region_id: int, type_id: int) -> list:
    if type_id in data_helper.market_history_dict[region_id]['history'].keys():
        if data_helper.market_history_dict[region_id]['history'][type_id]['updated']:
            # print('data found in dict')
            return data_helper.market_history_dict[region_id]['history'][type_id]['data']
    else:
        data_helper.market_history_dict[region_id]['history'][type_id] = dict()
        data_helper.market_history_dict[region_id]['history'][type_id]['updated'] = False

    return direct_market_api_functions.get_item_market_history_of_region(region_id, type_id)


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


def get_orders_of_all_region_from_api_multi(thread_num=20):
    """
    获得全部星域市场的订单

    :param thread_num: 线程数
    :return: 字典
    """
    region_list = data_helper.region_id_dict.keys()
    # region_list = [10000002, 10000011]
    get_all_orders_task = multithread_functions.MyGetTask(region_list)
    threads = [multithread_functions.MyGetOrdersOfAllRegionsThread(get_all_orders_task) for i in range(thread_num)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for region_id in get_all_orders_task.result_dict.keys():
        if len(get_all_orders_task.result_dict[region_id]) > 0:
            # print(region_id)
            multithread_functions.write_json_into_file_multi_thread('data/markets/{}'.format(region_id), 'order.json',
                                                                    get_all_orders_task.result_dict[region_id])
            # data_helper.write_json_into_file('data/markets/{}'.format(region_id), 'order.json',
            #                                  get_all_orders_task.result_dict[region_id])
    # print(get_all_orders_task)


def get_active_order_in_region_multi(region_id:int, thread_num=20):
    """
    获得星域市场订单

    :param region_id: 星域ID
    :param thread_num: 线程数
    :return: {type_id_1:[{order}, {}, ...], typer_id_2:...}
    """
    type_list_active_in_region = direct_market_api_functions.get_type_ids_have_active_order_in_region(region_id)
    task = multithread_functions.MyGetTask(type_list_active_in_region, region_id)
    threads = [multithread_functions.MyGetCurrentOrderInRegionThread(task, i) for i in range(thread_num)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    sorted_result_list = sorted(task.result_dict.items(), key=lambda x:len(x[1]), reverse=True)
    return sorted_result_list


def get_profitable_order_in_region(region_id: int, tax_rate=0.05, thread_num=20):
    """
    返回星域市场内可以赚取价差的订单

    :param region_id: 星域ID
    :param thread_num: 获取同时商品订单的线程数
    :return: {type_id_1:{'buy':[{},{},...],'sell':[{},{},...]}, type_id_2:...}
    """
    r, so_list, bo_list = dict(), list(), list()
    tmp = get_active_order_in_region_multi(region_id, thread_num)
    for type_id, orders in tmp:
        for o in orders:
            if o['is_buy_order']:
                bo_list.append(o)
            else:
                so_list.append(o)
            bo_list.sort(key=lambda x:x['price'], reverse=True)
            so_list.sort(key=lambda x:x['price'], reverse=False)

            if len(bo_list) > 0 and len(so_list) > 0 and bo_list[0]['price']*(1-tax_rate) > so_list[0]['price']:
                r[type_id] = {'buy':bo_list, 'sell':so_list}
        so_list, bo_list = list(), list()
    return r


def get_profitable_order(order_dict: dict, tax_rate=0.05):
    """
    返回所有星域市场范围内可以赚取价差的订单

    :param order_dict: {type_id_1:[{order}, {}, ...], typer_id_2:...}, 形式与get_active_order_in_region_multi()返回一致
    :param thread_num: 获取同时商品订单的线程数
    :return: {type_id_1:{'buy':[{},{},...],'sell':[{},{},...]}, type_id_2:...}
    """
    r, so_list, bo_list = dict(), list(), list()
    # tmp = get_active_order_in_region_multi(region_id, thread_num)
    for type_id, orders in order_dict.items():
        for o in orders:
            if o['is_buy_order']:
                bo_list.append(o)
            else:
                so_list.append(o)
            bo_list.sort(key=lambda x:x['price'], reverse=True)
            so_list.sort(key=lambda x:x['price'], reverse=False)

            if len(bo_list) > 0 and len(so_list) > 0 and bo_list[0]['price']*(1-tax_rate) > so_list[0]['price']:
                r[type_id] = {'buy':bo_list, 'sell':so_list}
        so_list, bo_list = list(), list()
    return r


def get_pure_profit_orders(p_order: dict, tax_rate=0.05, profit_bar=0):
    """
    获取各差价订单总利润

    :param p_order: {type_id_1:{'buy':[{},{},...],'sell':[{},{},...]}, type_id_2:...}, get_profitable_order得到的字典
    :param tax_rate: 空间站销售税率
    :return:
    """
    r_dict = dict()
    sell_n, buy_n = 0, 0
    for type_id, bns_orders in p_order.items():
        # print("{} {}".format(type_id, data_helper.get_value_type_id_dict(type_id)))
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
        tmp_order = None
        while (not sell_q.empty() and not buy_q.empty()) or (sell_n != 0 or buy_n != 0): # 订单队列不为空，或者
            if (sell_q.empty() and sell_n == 0) or (buy_q.empty() and buy_n == 0):
                break
            profit_single = 0
            if buy_n == 0:
                buy_order = buy_q.get()
                buy_n = buy_order['volume_remain']
            if sell_n == 0:
                sell_order = sell_q.get()
                sell_n = sell_order['volume_remain']
            profit_single = buy_order['price'] * (1-tax_rate) - sell_order['price']
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
        if profit_sum > profit_bar:
            r_dict[type_id] = {'type_name': data_helper.get_value_type_id_dict(type_id), 'profit': profit_sum,
                               'buy_order_num': len(buy_list), 'sell_order_num': len(sell_list), 'volume': volume,
                               'cost': cost, 'profit_rate': profit_sum/cost, 'buy': buy_list, 'sell': sell_list,
                               'recommendation_index': profit_sum/cost/(len(buy_list)+len(sell_list))}

    # sort_list = sorted(r_dict.items(), key=lambda x:x[1]['profit'], reverse=True)
    sort_list = sorted(r_dict.items(), key=lambda x:x[1]['recommendation_index'], reverse=True)
    return sort_list


def interstellar_logistic(tax_rate=0.05, profit_bar=0):
    allinone_order_dict = dict()
    if data_helper.market_order_dict is None:
        pass
    for orders in data_helper.market_order_dict.values():
        for order in orders:
            if order['type_id'] not in allinone_order_dict.keys():
                allinone_order_dict[order['type_id']] = list()
            allinone_order_dict[order['type_id']].append(order)

    tmp = get_profitable_order(allinone_order_dict)
    pure_profit_manifest = get_pure_profit_orders(tmp, tax_rate, profit_bar)
    return pure_profit_manifest


if __name__ == '__main__':
    # get_active_order_in_region_multi(10000011)

    #
    # orange = 3
    # r = get_profitable_order_in_region(10000002, 50)
    # if len(r) > 0:
    #     for type_id, bns_orders in r.items():
    #         print("{} {}".format(type_id, data_helper.get_value_type_id_dict(type_id)))
    #         for k, v in bns_orders.items():
    #             if k == 'buy':
    #                 vrange = len(v) if len(v) < orange else orange
    #                 for oi in reversed(range(vrange)):
    #                     print("buy{} {}".format(oi+1, v[oi]))
    #             elif k == 'sell':
    #                 vrange = len(v) if len(v) < orange else orange
    #                 for si in range(vrange):
    #                     print("sell{} {}".format(si+1, v[si]))

    # r = get_profitable_order_in_region(10000002, 0.05, 50)
    # # print("get_profitable_order_in_region: ".format(len(r)))
    # # print(r)
    # if len(r) > 0:
    #     r = get_pure_profit_orders(r, 0.05)
    #     lrange = len(r) if len(r) < 5 else 5
    #     for i in range(lrange):
    #         print(r[i])

    # get_orders_of_all_region_from_api_multi()

    # d = data_helper.market_order_dict
    # id(d)
    get_orders_of_all_region_from_api_multi()
    # print('orders updated.')
    # pure_profit_manifest = interstellar_logistic(profit_bar=10000000)
    print(1)
    pass
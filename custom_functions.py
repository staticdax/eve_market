#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-
import queue

import direct_market_api_functions
import data_helper
import multithread_functions
from datetime import datetime, timedelta
from memory_profiler import profile


def get_item_market_history_of_region_from_api_or_local(region_id: int, type_id: int) -> list:
    if type_id in data_helper.market_history_dict[region_id]['history'].keys():
        if data_helper.market_history_dict[region_id]['history'][type_id]['updated']:
            # 直接从文件载入的updated都是都是False, 更新过API的数据就为True
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


#@profile
def renew_region_markets_orders_dict_from_api_multi(thread_num=20):
    """
    获得全部星域市场的订单，更新data_helper.market_orders_dict

    :param thread_num: 线程数
    :return: 无返回值，更新data_helper.region_markets_orders_dict {regoin_id_1:[{order_1},...], region_id_2:[{},...], ...}
    """
    region_list = data_helper.region_id_dict.keys()
    # region_list = [10000002, 10000011]
    if len(data_helper.region_markets_orders_dict) > 0:
        data_helper.region_markets_orders_dict = dict()
    get_all_orders_task = multithread_functions.MyGetTask(region_list)
    threads = [multithread_functions.MyGetOrdersOfAllRegionsThread(get_all_orders_task) for i in range(thread_num)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for region_id, order_list in get_all_orders_task.result_dict.items():
        if len(order_list) > 0:
            data_helper.region_markets_orders_dict[region_id] = order_list

    # del threads

    # renew_all_orders_by_typeid_dict()
    # renew_all_profitable_orders_dict()


#@profile
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


def get_profitable_order_in_region_todo(region_id: int, tax_rate=0.05, thread_num=20):
    """
    返回星域市场内可以赚取价差的订单
    TODO: 重写

    :param region_id: 星域ID
    :param tax_rate: 销售税率
    :param thread_num: 获取同时商品订单的线程数
    :return: {type_id_1:{'buy':[{},{},...],'sell':[{},{},...]}, type_id_2:...}
    """
    # r = dict()
    # tmp = get_active_order_in_region_multi(region_id, thread_num)
    # for type_id, orders in tmp:
    #     so_list, bo_list = list(), list()
    #     for o in orders:
    #         if o['is_buy_order']:
    #             bo_list.append(o)
    #         else:
    #             so_list.append(o)
    #         bo_list.sort(key=lambda x: x['price'], reverse=True)
    #         so_list.sort(key=lambda x: x['price'], reverse=False)
    #
    #         if len(bo_list) > 0 and len(so_list) > 0 and bo_list[0]['price'] * (1 - tax_rate) > so_list[0]['price']:
    #             r[type_id] = {'buy': bo_list, 'sell': so_list}
    # return r


# def get_single_type_sorted_bns_orders_dict(orders_dict: dict):
#     """
#
#     :param orders_dict: 单个种类的bns_orders_dict {'buy':[{order_1},{order_2},...],'sell':[{order_1}, ...]}
#     :return: 买单按价格降序排列，卖单价格按升序排列
#     """
#     orders_dict['buy'].sort(key=lambda x: x['price'], reverse=True)
#     orders_dict['sell'].sort(key=lambda x: x['price'], reverse=False)


def get_profitable_order(order_dict: dict, tax_rate=0.05):
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

    :param profitable_bns_orders_dict: get_profitable_order()得到的字典
    {type_id_1:{'buy':[{order_1},{order_2},...],'sell':[{order_1}, ...]}, type_id_2:...}
    :param tax_rate: 空间站销售税率
    :param profit_min: 最低利润
    :return: profitable_orders_dict {type_id_1:{info1:info, info2:info, ..., buy:[{order}, ...]}, sell:[{order}, ...]}
    """
    profitable_orders_dict = dict()
    for type_id, bns_orders in profitable_bns_orders_dict.items():
        # print("{} {}".format(type_id, data_helper.get_type_name(type_id)))
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
            profitable_orders_dict[type_id] = {'type_name': data_helper.get_type_name(type_id),
                                               'profit': profit_sum,
                                               'buy_order_num': len(buy_list),
                                               'sell_order_num': len(sell_list),
                                               'volume': volume,
                                               'cost': cost,
                                               'profit_rate': profit_sum / cost,
                                               'buy': buy_list,
                                               'sell': sell_list,
                                               'rating': profit_sum / cost / (len(buy_list) + len(sell_list))}
    return profitable_orders_dict
    # pure_profit_sorted_list = sorted(profitable_orders_dict.items(), key=lambda x:x[1]['profit'], reverse=True)
    # pure_profit_sorted_list = sorted(profitable_orders_dict.items(),
    #                                  key=lambda x: x[1]['rating'], reverse=True)
    # return pure_profit_sorted_list


#@profile
def renew_all_profitable_orders_dict(tax_rate=0.05, min_profit=0):  # interstellar_logistic
    """
    更新data_helper.all_profitable_orders_dict
    {type_id_1:{info1:info, info2:info, ..., buy:[{order}, ...], sell:[{order}, ...]}, type_id_2: {...}, ...}

    :param tax_rate: 销售税率
    :param min_profit: 最小利润
    :return:
    """
    profitable_bns_orders_dict = get_profitable_order(data_helper.all_orders_by_typeid_dict)
    data_helper.all_profitable_orders_dict = get_detailed_profitable_orders_dict(profitable_bns_orders_dict,
                                                                                 tax_rate, min_profit)


#@profile
def get_profitable_orders_sorted_dict(profitable_orders_dict: dict, min_profit=0, sorted_by='rating', reverse=True):
    """
    对profitable_orders_dict进行排序，过滤，

    :param profitable_orders_dict: data_helper.all_profitable_orders_dict 或 data_helper.region_profitable_orders_dict
        {type_id_1: {'type_name': info, 'profit': info, ..., 'buy': [{order}, ...], 'sell': [{order}, ...]}, type_id_2: {...}, ...}
    :param min_profit: 最小利润
    :param sorted_by: 排序依据，可选'profit', 'buy_order_num', 'sell_order_num', 'volume', 'cost', 'profit_rate', 'rating'
    :param reverse: 是否降序排序，默认为降序排序
    :return:
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


if __name__ == '__main__':
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

    # renew_region_markets_orders_dict_from_api_multi()
    # print('orders updated.')

    #
    renew_region_markets_orders_dict_from_api_multi()
    # renew_all_orders_by_typeid_dict()
    # print('orders updated from file.')
    renew_all_profitable_orders_dict()
    r = get_profitable_orders_sorted_dict(data_helper.all_profitable_orders_dict, min_profit=50000000,
                                          sorted_by='rating', reverse=True)
    pass
    # data_helper.write_json_into_file('data/test', 'all_profitable_orders_dict.json',
    #                                  data_helper.all_profitable_orders_dict)
    pass

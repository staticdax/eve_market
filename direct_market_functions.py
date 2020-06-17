#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import requests
import json
import data_helper
from datetime import datetime, timedelta

# VERSION = 'dev'
VERSION = 'latest'
API_URL = 'https://esi.evepc.163.com/' + VERSION
MARKET_URL = 'markets'
DATA_SOURCE = 'datasource=serenity'

class RequestParamDefault:
    def __init__(self):
        self.params = dict()
        self.params['datasource'] = 'serenity'


def get_market_orders(region_id: int, order_type ='buy', page = 1, type_id = -1):
    """
    返回星域市场订单数据

    :param region_id: 星域ID
    :param order_type: 买单或卖单，buy/sell/all可选
    :param page: 页数
    :param type_id: 商品id
    :return: json格式解码得到的一个关于市场顶大的字典数组，持续日期duration，订单类型is_buy_order，创建日期is_buy_order，
    订单所在的空间站位置ID location_id，成交最小量min_volume，订单ID order_id，商品价格price，
    订单有效范围range，星系ID system_id，商品ID type_id，商品剩余量volume_remain，商品总量volume_total
    """
    market_orders_list = []
    p = RequestParamDefault()
    p.params['order_type'] = order_type
    p.params['page'] = page
    p.params['type_id'] = '' if type_id == -1 else order_type

    request_url = "{api_url}/markets/{regionid}/orders/".format(api_url = API_URL, regionid = region_id)
    r = requests.get(request_url, p.params)
    # 添加获取多页结果，如get_type_ids_have_active_order_in_region()
    market_orders_list = r.json()

    if r.headers['X-Pages'] > 1:
        for i in range(2, int(r.headers['X-Pages']) + 1):
            p.params['page'] = i
            r = requests.get(request_url, p.params)
            if r.status_code == 200:
                market_orders_list += r.json

    return market_orders_list



def get_region_market_history(region_id: int, type_id: int):
    """
    返回星域市场的历史数据

    :param region_id: 星域id
    :param type_id: 商品id
    :return: json格式解码得到的一个关于商品的历史数据的字典数组，包括日期，平均价格，最高价，最低价，成交订单数，成交量
    """
    p = RequestParamDefault()
    p.params['type_id'] = type_id
    request_url = "{api_url}/markets/{regionid}/history/".format(api_url = API_URL, regionid = region_id)
    r = requests.get(request_url, p.params)
    if r.status_code == 200:
        return r.json()
    else:
        print("[Debug] region_id: {}; type_id: {}\nstatus: {}\ncontent: {}\n".format(region_id, type_id, r.status_code, r.content))
        return []


def get_last_n_day_volume(region_id: int, type_id: int, n: int):
    """
    得到最近N天的成交量

    :param region_id: 星域id
    :param type_id: 商品id
    :param n: 最近n天
    :return: 总成交量
    """
    volume_sum = 0
    trade_history_list = get_region_market_history(region_id, type_id)
    if len(trade_history_list) == 0:
        return volume_sum
    print(trade_history_list)
    minus_n_date = datetime.strptime(trade_history_list[-1]['date'], '%Y-%m-%d') - timedelta(n)
    check_pos_date = datetime.strptime(trade_history_list[-n]['date'], '%Y-%m-%d') if len(trade_history_list) > n \
        else datetime.strptime(trade_history_list[0]['date'], '%Y-%m-%d')
    time_delta = check_pos_date - minus_n_date
    if time_delta.days == 0:    # 最后n个记录和最后n天都一一对应
        trade_history_list = trade_history_list[-n:]
    elif time_delta.days < 0:        # 最后n个记录不和最后n天都一一对应，最后n天可能不是每天都有交易记录，最后n个记录可能是最后n+m天内的记录
        for i in range(1, n):   # 从后往前搜索，找到第一个不在最后n天范围内的记录，删除不需要的记录
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


def get_last_n_day_orders(region_id: int, type_id: int, n: int):
    """
    得到最近N天的成交量

    :param region_id: 星域id
    :param type_id: 商品id
    :param n: 最近n天
    :return: 总成交量
    """
    order_sum = 0
    trade_history_list = get_region_market_history(region_id, type_id)
    if len(trade_history_list) == 0:
        return order_sum
    # print(trade_history_list)
    minus_n_date = datetime.strptime(trade_history_list[-1]['date'], '%Y-%m-%d') - timedelta(n)
    check_pos_date = datetime.strptime(trade_history_list[-n]['date'], '%Y-%m-%d') if len(trade_history_list) > n \
        else datetime.strptime(trade_history_list[0]['date'], '%Y-%m-%d')
    time_delta = check_pos_date - minus_n_date
    if time_delta.days == 0:    # 最后n个记录和最后n天都一一对应
        trade_history_list = trade_history_list[-n:]
    elif time_delta.days < 0:        # 最后n个记录不和最后n天都一一对应，最后n天可能不是每天都有交易记录，最后n个记录可能是最后n+m天内的记录
        for i in range(1, n):   # 从后往前搜索，找到第一个不在最后n天范围内的记录，删除不需要的记录
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


def get_type_ids_have_active_order_in_region(region_id: int):
    """
    星域中有活跃订单的商品id

    :param region_id: 星域ID
    :return: 星域中有活跃订单的商品id列表
    """
    type_id_list = []
    p = RequestParamDefault()
    p.params['page'] = 1
    request_url = "{api_url}/markets/{regionid}/types/".format(api_url=API_URL, regionid=region_id)
    r = requests.get(request_url, p.params)
    type_id_list = r.json()

    if int(r.headers['X-Pages']) > 1:
        for i in range(2, int(r.headers['X-Pages']) + 1):
            p.params['page'] = i
            r = requests.get(request_url, p.params)
            if r.status_code == 200:
                type_id_list += r.json()

    return type_id_list


def main():

    # r = requests.get('https://esi.evepc.163.com/latest/markets/10000002/orders/?datasource=serenity&order_type=buy&page=1')
    # print(r.json())
    # print(len(r.json()))
    # print(json.dumps(r.json()[0]))
    # print(type(r.json()))
    # print(type(r.json()[0]))
    # print(get_market_orders(10000002))

    # print(get_region_market_history(10000002, 34))
    n = 7
    type_id = 34
    region_id = 10000002


    sum = get_last_n_day_volume(region_id, type_id, n)
    print("商品 #{} 在 {} 最近 {} 天总成交量为 {:,} ".format(type_id, data_helper.region_id_dict[region_id], n, sum))
    l = get_type_ids_have_active_order_in_region(region_id)
    print(l)
    print("len(get_type_ids_have_active_order_in_region(region_id)): {}".format(len(l)))
    # if len(l) == 0:
    #     return

    # volume_sum_dict = dict()
    # for i in l:
    #     sum = get_last_n_day_volume(region_id, i, n)
    #     volume_sum_dict[i] = sum
    #
    # max_volume = max(list(volume_sum_dict.values()))
    # max_type = [k for (k,v) in volume_sum_dict.items() if v == max_volume]
    # for _ in max_type:
    #     print("商品 #{} 在 {} 最近 {} 天总成交量为 {:,} ".format(_, region_id, n, volume_sum_dict[_]))




if __name__ == '__main__':
    main()


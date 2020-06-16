#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import requests
import json
import load_data
from datetime import datetime, timedelta


API_URL = 'https://esi.evepc.163.com/latest'
MARKET_URL = 'markets'
DATA_SOURCE = 'datasource=serenity'

class RequestParamDefault:
    def __init__(self):
        self.params = dict()
        self.params['datasource'] = 'serenity'


def get_market_order(region_id: int, order_type = 'buy', page = 1, type_id = -1):
    p = RequestParamDefault()
    p.params['order_type'] = order_type
    p.params['page'] = page
    p.params['type_id'] = '' if type_id == -1 else order_type
    # https://esi.evepc.163.com/latest/markets/10000002/orders/?datasource=serenity&order_type=buy&page=200
    # request_url = "{api_url}{market_url}/{regionid}/orders/?{data_source}&order_type={ordertype}&page={page}"\
    #     .format(api_url = API_URL, market_url = MARKET_URL, regionid = region_id, data_source = DATA_SOURCE, \
    #             ordertype = order_type, page = page)
    request_url = "{api_url}/markets/{regionid}/orders/".format(api_url = API_URL, regionid = region_id)
    r = requests.get(request_url, p.params)
    return r.json()

def get_region_market_history(region_id: int, type_id: int):
    """
    返回星域市场的历史数据

    :param region_id: 星域id
    :param type_id: 商品id
    :return: json格式的商品的历史数据，包括日期，平均价格，最高价，最低价，成交订单数，成交量
    """
    p = RequestParamDefault()
    p.params['type_id'] = type_id
    request_url = "{api_url}/markets/{regionid}/history/".format(api_url = API_URL, regionid = region_id)
    r = requests.get(request_url, p.params)
    return r.json()


def get_last_N_day_volume(region_id: int, type_id: int, n: int):
    """
    得到最近N天的成交量

    :param region_id: 星域id
    :param type_id: 商品id
    :param n: 最近n天
    :return: 总成交量
    """
    trade_history_list = get_region_market_history(region_id, type_id)
    print(trade_history_list)
    minus_n_date = datetime.now() - timedelta(n)
    check_pos_date = datetime.strptime(trade_history_list[-n]['date'], '%Y-%m-%d')
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
    volume_sum = 0
    # print(type_id)
    for _ in trade_history_list:
        # print("{} _['volume']: {}".format(_['date'], _['volume']))
        volume_sum += _['volume']
    return volume_sum


def get_type_ids_have_active_order_in_region(region_id: int):
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
            type_id_list.append(r.json())

    return type_id_list



def main():
    system_id_dict = load_data.load_system_id()
    constellation_id_dict = load_data.load_constellation_id()
    region_id_dict = load_data.load_region_id()
    system_constellation_dict = load_data.load_system_constellation()
    constellation_region_dict = load_data.load_constellation_region()
    # r = requests.get('https://esi.evepc.163.com/latest/markets/10000002/orders/?datasource=serenity&order_type=buy&page=1')
    # print(r.json())
    # print(len(r.json()))
    # print(json.dumps(r.json()[0]))
    # print(type(r.json()))
    # print(type(r.json()[0]))
    # print(get_market_order(10000002))

    # print(get_region_market_history(10000002, 34))
    n = 7
    type_id = 34
    region_id = 10000002


    sum = get_last_N_day_volume(region_id, type_id, n)
    print("商品 #{} 在 {} 最近 {} 天总成交量为 {:,} ".format(type_id, region_id_dict[region_id], n, sum))
    # l = get_type_ids_have_active_order_in_region(region_id)
    # print(l)
    # print("len(get_type_ids_have_active_order_in_region(region_id)): {}".format(len(l)))
    # if len(l) == 0:
    #     return

    # volume_sum_dict = dict()
    # for i in l:
    #     sum = get_last_N_day_volume(region_id, i, n)
    #     volume_sum_dict[i] = sum
    #
    # max_volume = max(list(volume_sum_dict.values()))
    # max_type = [k for (k,v) in volume_sum_dict.items() if v == max_volume]
    # for _ in max_type:
    #     print("商品 #{} 在 {} 最近 {} 天总成交量为 {:,} ".format(_, region_id, n, volume_sum_dict[_]))




if __name__ == '__main__':
    main()


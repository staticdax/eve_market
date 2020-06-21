#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import requests
import data_helper

# VERSION = 'dev'
VERSION = 'latest'
API_URL = 'https://esi.evepc.163.com/' + VERSION
MARKET_URL = 'markets'
DATA_SOURCE = 'datasource=serenity'


class RequestParamDefault:
    def __init__(self):
        self.params = dict()
        self.params['datasource'] = 'serenity'


def get_orders_of_region_one_page_raw_response(region_id: int, order_type='all', page=1, type_id=-1) -> requests.Response:
    """
    返回星域市场订单数据，单线程，仅返回指定页数的结果

    :param region_id: 星域ID
    :param order_type: 买单或卖单，buy/sell/all可选
    :param page: 页数
    :param type_id: 商品id
    :return: requests.Response实例
    """
    p = RequestParamDefault()
    p.params['order_type'] = order_type
    p.params['page'] = page
    p.params['type_id'] = '' if type_id == -1 else type_id

    request_url = "{api_url}/markets/{regionid}/orders/".format(api_url=API_URL, regionid=region_id)
    r = requests.get(request_url, p.params)

    return r


def get_orders_of_region_single_thread(region_id: int, order_type='all', page=1, type_id=-1) -> list:
    """
    返回星域市场订单数据，单线程，从指定页数开始，尾页结束。拼接每页结果到一个大列表

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
    p.params['type_id'] = '' if type_id == -1 else type_id

    request_url = "{api_url}/markets/{regionid}/orders/".format(api_url=API_URL, regionid=region_id)
    r = requests.get(request_url, p.params)

    if r.status_code == 200:
        market_orders_list = r.json()

        if int(r.headers['X-Pages']) > 1:
            for i in range(page + 1, int(r.headers['X-Pages']) + 1):
                p.params['page'] = i
                r = requests.get(request_url, p.params)
                if r.status_code == 200:
                    market_orders_list += r.json()
    else:
        print("[Debug] request_url: {}\nrequest_params: {}\nregion_id: {}; type_id: {}\nstatus: {}\ncontent: {}\n".
              format(request_url, p.params, region_id, type_id, r.status_code, r.content))
        return []

    return market_orders_list


def get_item_market_history_of_region(region_id: int, type_id: int) -> list:
    """
    返回星域市场的历史数据

    :param region_id: 星域id
    :param type_id: 商品id
    :return: json格式解码得到的一个关于商品的历史数据的字典数组，包括日期，平均价格，最高价，最低价，成交订单数，成交量
    """
    p = RequestParamDefault()
    p.params['type_id'] = type_id
    request_url = "{api_url}/markets/{regionid}/history/".format(api_url=API_URL, regionid=region_id)
    r = requests.get(request_url, p.params)

    if r.status_code == 200:
        data_helper.update_market_history_dict(region_id, type_id, r.json())
        data_helper.write_json_into_file('data/markets/{}/history'.format(region_id),
                                         '{}.json'.format(type_id), r.json())
        return r.json()
    elif r.status_code == 404:
        print("found unknown typeid {} in history. Add to unknown_type_id_queue...".format(type_id))
        # data_helper.get_unknown_type_id_info_n_update_dict(type_id)
        data_helper.unknown_type_id_queue.put(type_id)
        # test_listener.
        return []
    else:
        print("[Debug] request_url: {}\nrequest_params: {}\nregion_id: {}; type_id: {}\nstatus: {}\ncontent: {}\n".
              format(request_url, p.params, region_id, type_id, r.status_code, r.content))
        return []


def get_type_ids_have_active_order_in_region(region_id: int) -> list:
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

    if r.status_code == 200:
        type_id_list = r.json()

        if int(r.headers['X-Pages']) > 1:
            for i in range(2, int(r.headers['X-Pages']) + 1):
                p.params['page'] = i
                r = requests.get(request_url, p.params)
                if r.status_code == 200:
                    type_id_list += r.json()
    else:
        print("[Debug] request_url: {}\nrequest_params: {}\nregion_id: {}\nstatus: {}\ncontent: {}\n".
              format(request_url, p.params, region_id, r.status_code, r.content))

    return type_id_list


def main():
    # r = requests.get('https://esi.evepc.163.com/latest/markets/10000002/orders/?datasource=serenity&order_type=buy&page=1')
    # print(r.json())
    # print(len(r.json()))
    # print(json.dumps(r.json()[0]))
    # print(type(r.json()))
    # print(type(r.json()[0]))
    # print(get_orders_of_region_single_thread(10000002))

    # print(get_item_market_history_of_region(10000002, 34))
    # n = 7
    # type_id = 34
    # region_id = 10000002
    # region_id = 10000002
    # print(get_item_market_history_of_region(region_id, type_id))
    #
    # sum = get_last_n_day_volume(region_id, type_id, n)
    # print("商品 #{} 在 {} 最近 {} 天总成交量为 {:,} ".format(type_id, data_helper.region_id_dict[region_id], n, sum))
    # l = get_type_ids_have_active_order_in_region(region_id)
    # print(l)
    # print("len(get_type_ids_have_active_order_in_region(region_id)): {}".format(len(l)))
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
    n = 7
    # type_id = 34
    # type_id = 213
    # region_id = 10000002
    # region_id = 10000011
    # print(get_item_market_history_of_region(region_id, type_id))
    # print(get_orders_of_region_single_thread(10000002, type_id=34))
    # get_orders_of_region_single_thread(10000001)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import json
import os
import requests
import queue

FUZZWORK_URL = 'https://www.fuzzwork.co.uk/api/typeid.php'


market_history_dict = dict()
region_markets_orders_dict = dict()
all_orders_by_typeid_dict = dict()
all_profitable_orders_dict = dict()
region_profitable_orders_dict = dict()
tmp_dict = dict()
tmp_list = list()

region_id_dict = dict()
constellation_id_dict = dict()
system_id_dict = dict()
location_id_dict = dict()
constellation_region_dict = dict()
system_constellation_dict = dict()
location_system_dict = dict()

type_id_dict = dict()
unknown_type_id_queue = queue.Queue()


def load_region_id():
    """
    加载含有星域id和星域名称的json文件，更新region_id_dict(星域id为键，名称为值的字典)

    :return:
    """
    with open('data/region_id.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        region_id_dict[_['region_id']] = _['region']


def load_constellation_id():
    """
    加载含有星座id和星域名称的json文件，更新constellation_id_dict(星座id为键，名称为值的字典)

    :return:
    """
    with open('data/constellation_id.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        constellation_id_dict[_['constellation_id']] = _['constellation']


def load_constellation_region():
    """
    加载含有星座id和星域id的json文件，更新constellation_region_dict(星座id为键，星域id为值的字典)

    :return:
    """
    with open('data/constellation_region.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        constellation_region_dict[_['constellation_id']] = _['region_id']


def load_system_id():
    """
    加载含有星系id和星系名称的json文件，更新system_id_dict(星系id为键，星系名称为值的字典)

    :return:
    """
    with open('data/system_id.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        system_id_dict[_['system_id']] = _['system']


def load_system_constellation():
    """
    加载含有星系id和星座id的json文件，更新system_constellation_dict(星系id为键，星座id为值的字典)

    :return:
    """
    with open('data/system_constellation.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        system_constellation_dict[_['system_id']] = _['constellation_id']


def load_location_id():
    """
    加载含有空间站id和空间站名称的json文件，更新location_id_dict(空间站id为键，空间站名称为值的字典)

    :return:
    """
    with open('data/location_id.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        location_id_dict[_['location_id']] = _['location']


def load_location_system():
    """
    加载含有空间站id和星系id的json文件，更新location_system_dict(空间站id为键，星系id为值的字典)

    :return:
    """
    with open('data/location_system.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for _ in j:
        location_system_dict[_['location_id']] = _['system_id']


def load_type_id():
    """
    加载物品type_id和物品名称，更新type_id_dict(type_id为键，type_name为值的字典)

    :return:
    """
    with open('data/type_id.json', 'r', encoding='utf-8') as f:
        j = json.load(f)
    for k, v in j.items():
        type_id_dict[int(k)] = v


def get_type_name(type_id: int):
    if validate_type_id(type_id):
        return type_id_dict[type_id]
    else:
        print("Todo: try to request FUZZWORK")
        return "unknown item"
    # try:
    #     return type_id_dict[type_id]
    # except KeyError as e:
    #     print(e)
    #     print("Todo: try to request FUZZWORK")
    #     return "unknown item"


def get_location_name(location_id: int):
    if validate_location_id(location_id):
        return location_id_dict[location_id]
    return "UNKNOWN LOCATION"


def get_system_name(system_id: int):
    if validate_system_id(system_id):
        return system_id_dict[system_id]
    return "UNKNOWN SYSTEM"


def get_constellation_name(constellation_id: int):
    if validate_constellation_id(constellation_id):
        return constellation_id_dict[constellation_id]
    return "UNKNOWN CONSTELLATION"


def get_region_name(region_id: int):
    if validate_region_id(region_id):
        return region_id_dict[region_id]
    return "UNKNOWN REGION"


def validate_region_id(region_id: int):
    if region_id in region_id_dict:
        return True
    return False


def validate_region_name(region_name: str):
    if region_name in region_id_dict.values():
        return True
    return False


def validate_constellation_id(constellation_id: int):
    if constellation_id in constellation_id_dict:
        return True
    return False


def validate_constellation_name(constellation: str):
    if constellation in constellation_id_dict.values():
        return True
    return False


def validate_system_id(system_id: int):
    if system_id in system_id_dict:
        return True
    return False


def validate_system_name(system: str):
    if system in system_id_dict.values():
        return True
    return False


def validate_location_id(location_id: int):
    if location_id in location_id_dict:
        return True
    return False


def validate_location_name(location: str):
    if location in location_id_dict.values():
        return True
    return False


def validate_type_id(type_id: int):
    if type_id in type_id_dict:
        return True
    return False


def validate_type_name(type_name: str):
    if type_name in type_id_dict.values():
        return True
    return False


def write_json_into_file(file_path: str, file_name: str, content: list):
    if not os.path.exists(file_path):
        os.makedirs(file_path, 0o755)
    with open(os.path.join(file_path, file_name), 'w') as f:
        json.dump(content, f)
    print("file {} renewed".format(os.path.join(file_path, file_name)))


def get_unknown_type_id_info_n_update_dict(type_id: int):
    if type_id in type_id_dict.keys():
        return False
    params = dict()
    params['typeid'] = type_id
    try:
        r = requests.get(FUZZWORK_URL, params)
        # t = MyRequstsThread(FUZZWORK_URL, params)
        # r = t.start()
    except Exception as e:
        print(e)
        return False
    # print(r.text)
    # print(r.json())
    if r.status_code == 200 and r.json()['typeName'] != 'bad item':
        type_id_dict[type_id] = r.json()['typeName']
        return True


def rewrite_type_id_json_file():
    if len(type_id_dict) > 1:
        with open('data/type_id.json', 'w', encoding='utf-8') as f:
            json.dump(type_id_dict, f)


def load_market_history_dict_from_json():
    # region_id_dict = load_region_id()
    # market_history_dict = dict()
    for region_id in region_id_dict.keys():
        market_history_dict[region_id] = dict()
        market_history_dict[region_id]['history'] = dict()
    for region_id in region_id_dict.keys():
        dir_name = "data/markets/{}/history".format(region_id)
        for root, dirs, files in os.walk(dir_name):
            for file in files:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        type_id = file.strip('.json')
                        if region_id not in market_history_dict.keys():
                            market_history_dict[region_id] = dict()
                        if 'history' not in market_history_dict[region_id].keys():
                            market_history_dict[region_id]['history'] = dict()
                        market_history_dict[region_id]['history'][type_id] = dict()
                        market_history_dict[region_id]['history'][type_id]['updated'] = False
                        market_history_dict[region_id]['history'][type_id]['data'] = json.load(f)
                    except Exception as e:
                        print('Exception in load_market_history_dict_from_json()')
                        print(e)
    # return market_history_dict


def load_market_order_dict_from_json():
    """
    从文件读取json，返回全部星域市场的订单数据

    :return: {region_id_1:[{order}, {}, ...], region_id_2:[], ...}
    """
    # region_id_dict = load_region_id()
    order_dict = dict()
    for region_id in region_id_dict.keys():
        file_name = 'data/markets/{}/order.json'.format(region_id)
        try:
            if os.path.exists(file_name):
                with open(file_name, 'r', encoding='utf-8') as f:
                    order_dict[region_id] = json.load(f)
        except Exception as e:
            print(e)
            print('Exception: load_market_order_dict_from_json')
            print('You may need to renew/delete {}'.format(file_name))

    return order_dict


def update_market_history_dict(region_id, type_id, r_json):
    market_history_dict[region_id]['history'][type_id]['data'] = r_json
    market_history_dict[region_id]['history'][type_id]['updated'] = True


def init_region_order_dict():
    # region_order_dict = dict()
    # for region_id in region_id_dict.keys():
    #     region_id_dict[region_id] = []
    # return region_id_dict
    for region in market_history_dict:
        region['order'] = dict()


load_region_id()
load_system_id()
load_constellation_id()
load_location_id()
load_system_constellation()
load_constellation_region()
load_location_system()
load_type_id()
load_market_history_dict_from_json()

# system_id_dict = load_system_id()
# constellation_id_dict = load_constellation_id()
# region_id_dict = load_region_id()
# system_constellation_dict = load_system_constellation()
# constellation_region_dict = load_constellation_region()
# type_id_dict = load_type_id()
# market_history_dict = load_market_history_dict_from_json()
# unknown_type_id_queue = queue.Queue()

# market_order_dict = load_market_order_dict_from_json()


def main():
    pass


if __name__ == '__main__':
    main()
    # add_unknown_type_id_2_file(32250)
    # print(get_unknown_type_id_info_n_update_dict(32250))
    # print(market_dict)
    # print(system_id_dict[30000001])

    # print(validate_region_id(10000002))
    # print(validate_type_id(18))
    # print(get_unknown_type_id_info_n_update_dict(32250))
    # print(validate_region_id(10000002))

    # location_id = 60005740
    # if validate_location_id(location_id):
    #     print(location_id_dict[location_id])

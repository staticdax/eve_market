#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import json
import os
import requests
import queue


FUZZWORK_URL = 'https://www.fuzzwork.co.uk/api/typeid.php'

def load_region_id():
    """
    加载含有星域id和星域名称的json文件，返回星域id为键，名称为值的字典

    :return: 星域id为键，名称为值的字典
    """
    with open('data/region_id.json', 'r') as f:
        j = json.load(f)

    region_id_dict = dict()
    for _ in j:
        region_id_dict[_['region_id']] = _['region']
    return region_id_dict


def load_constellation_id():
    """
    加载含有星座id和星域名称的json文件，返回星座id为键，名称为值的字典

    :return: 星座id为键，名称为值的字典
    """
    with open('data/constellation_id.json', 'r') as f:
        j = json.load(f)

    constellation_id_dict = dict()
    for _ in j:
        constellation_id_dict[_['constellation_id']] = _['constellation']
    return constellation_id_dict

def load_constellation_region():
    """
    加载含有星座id和星域id的json文件，返回星座id为键，星域id为值的字典

    :return: 星座id为键，星域id为值的字典
    """
    with open('data/constellation_region.json', 'r') as f:
        j = json.load(f)

    constellation_region_dict = dict()
    for _ in j:
        constellation_region_dict[_['constellation_id']] = _['region_id']
    return constellation_region_dict


def load_system_id():
    """
    加载含有星系id和星系名称的json文件，返回星系id为键，星系名称为值的字典

    :return: 星系id为键，星系名称为值的字典
    """
    with open('data/system_id.json', 'r') as f:
        j = json.load(f)

    system_id_dict = dict()
    for _ in j:
        system_id_dict[_['system_id']] = _['system']
    return system_id_dict


def load_system_constellation():
    """
    加载含有星系id和星座id的json文件，返回星系id为键，星座id为值的字典

    :return: 星系id为键，星座id为值的字典
    """
    with open('data/system_constellation.json', 'r') as f:
        j = json.load(f)

    system_constellation_dict = dict()
    for _ in j:
        system_constellation_dict[_['system_id']] = _['constellation_id']
    return system_constellation_dict


def load_type_id():
    """
    加载物品type_id和物品名称

    :return: type_id为键，type_name为值的字典
    """
    with open('data/type_id.json', 'r') as f:
        j = json.load(f)

    type_id_dict = dict()
    for k, v in j.items():
        type_id_dict[int(k)] = v
    return type_id_dict

def get_value_type_id_dict(type_id: int):
    try:
        return type_id_dict[type_id]
    except KeyError as e:
        print(e)
        print("Todo: try to request FUZZWORK")
        return "unknown item"

def validate_region_id(region_id: int):
    if region_id in region_id_dict:
        return True
    return False


def validate_region_name(region_name: str):
    if region_name in region_id_dict.values():
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
    region_id_dict = load_region_id()
    market_dict = dict()
    for region_id in region_id_dict.keys():
        market_dict[region_id] = dict()
        market_dict[region_id]['history'] = dict()
    for region_id in region_id_dict.keys():
        dir = "data/markets/{}/history".format(region_id)
        for root, dirs, files in os.walk(dir):
            for file in files:
                with open(os.path.join(root, file), 'r') as f:
                    try:
                        type_id = file.strip('.json')
                        if not region_id in market_dict.keys():
                            market_dict[region_id] = dict()
                        if not 'history' in market_dict[region_id].keys():
                            market_dict[region_id]['history'] = dict()
                        market_dict[region_id]['history'][type_id] = dict()
                        market_dict[region_id]['history'][type_id]['updated'] = False
                        market_dict[region_id]['history'][type_id]['data'] = json.load(f)
                    except Exception as e:
                        print('Exception in load_market_history_dict_from_json()')
                        print(e)
    return market_dict


def load_market_order_dict_from_json():
    region_id_dict = load_region_id()
    order_dict = dict()
    for region_id in region_id_dict.keys():
        dir = 'data/markets/{}/order.json'.format(region_id)
        try:
            if os.path.exists(dir):
                with open(dir, 'r') as f:
                    order_dict[region_id] = json.load(f)
        except Exception as e:
            print(e)
            print('Exception: load_market_order_dict_from_json')
            print('You may need to renew/delete {}'.format(dir))

    return order_dict


def update_market_history_dict(region_id, type_id, rjson):
    market_history_dict[region_id]['history'][type_id]['data'] = rjson
    market_history_dict[region_id]['history'][type_id]['updated'] = True


def init_region_order_dict():
    # region_order_dict = dict()
    # for region_id in region_id_dict.keys():
    #     region_id_dict[region_id] = []
    # return region_id_dict
    for region in market_history_dict:
        region['order'] = dict()





def main():
    # print(load_region_id())
    # print(load_constellation_id())
    # [k for (k, v) in region_id_dict.items() if v == '德里克']
    # l = load_constellation_region()
    # print(l)
    # print(l[20000001])
    # l = load_system_constellation()
    # print(l)
    # print(l[30000001])
    # print(load_system_id()[30000001])
    # l = load_type_id()
    # k = str(12301)
    # print(l[k])
    # print(region_id_dict)
    # print(validate_type_id('34'))
    # add_unknown_type_id_2_file(32250)
    pass

system_id_dict = load_system_id()
constellation_id_dict = load_constellation_id()
region_id_dict = load_region_id()
system_constellation_dict = load_system_constellation()
constellation_region_dict = load_constellation_region()
type_id_dict = load_type_id()
market_history_dict = load_market_history_dict_from_json()
# market_order_dict = load_market_order_dict_from_json()
market_history_dict = None
unknown_type_id_queue = queue.Queue()

if __name__ == '__main__':
    main()
    # add_unknown_type_id_2_file(32250)
    # print(get_unknown_type_id_info_n_update_dict(32250))
    # print(market_dict)
    # print(system_id_dict[30000001])

    # print(validate_region_id(10000002))
    # print(validate_type_id(18))
    # print(get_unknown_type_id_info_n_update_dict(32250))
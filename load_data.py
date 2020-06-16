#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import json


def load_region_id():
    """
    加载含有星域id和星域名称的json文件，返回星域id为键，名称为值的字典

    :return:
    """
    with open('./region_id.json', 'r') as f:
        j = json.load(f)

    region_id_dict = dict()
    for _ in j:
        region_id_dict[_['region_id']] = _['region']
    return region_id_dict


def load_constellation_id():
    """
    加载含有星座id和星域名称的json文件，返回星座id为键，名称为值的字典

    :return:
    """
    with open('./constellation_id.json','r') as f:
        j = json.load(f)

    constellation_id_dict = dict()
    for _ in j:
        constellation_id_dict[_['constellation_id']] = _['constellation']
    return constellation_id_dict

def load_constellation_region():
    """
    加载含有星座id和星域id的json文件，返回星座id为键，星域id为值的字典

    :return:
    """
    with open('./constellation_region.json','r') as f:
        j = json.load(f)

    constellation_region_dict = dict()
    for _ in j:
        constellation_region_dict[_['constellation_id']] = _['region_id']
    return constellation_region_dict


def load_system_id():
    """
    加载含有星系id和星系名称的json文件，返回星系id为键，星系名称为值的字典

    :return:
    """
    with open('./system_id.json','r') as f:
        j = json.load(f)

    system_id_dict = dict()
    for _ in j:
        system_id_dict[_['system_id']] = _['system']
    return system_id_dict


def load_system_constellation():
    """
    加载含有星系id和星座id的json文件，返回星系id为键，星座id为值的字典

    :return:
    """
    with open('./system_constellation.json','r') as f:
        j = json.load(f)

    system_constellation_dict = dict()
    for _ in j:
        system_constellation_dict[_['system_id']] = _['constellation_id']
    return system_constellation_dict

def main():
    # print(load_region_id())
    # print(load_constellation_id())
    # [k for (k, v) in region_id_dict.items() if v == '德里克']
    l = load_constellation_region()
    print(l)
    print(l[20000001])
    l = load_system_constellation()
    print(l)
    print(l[30000001])
    print(load_system_id()[30000001])
    pass


if __name__ == '__main__':
    main()
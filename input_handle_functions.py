#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import data_helper
import custom_functions
import direct_market_api_functions


def input_get_region_market_history():
    region_id = input("星域编号(default: 10000002): ")
    region_id = 10000002 if region_id == '' else int(region_id)
    # print(region_id)
    type_id = input("商品编号(default: 34): ")
    type_id = 34 if type_id == '' else int(type_id)
    # print(type_id)
    if data_helper.validate_region_id(region_id) and data_helper.validate_type_id(type_id):
        print("星域编号: {} 商品编号: {}".format(region_id, type_id))
        # r = direct_market_api_functions.get_item_market_history_of_region(region_id, type_id)
        r = custom_functions.get_item_market_history_of_region_from_api_or_local(region_id, type_id)
        for i in r:
            print(i)
    else:
        print('invalid input')
        print("validate_region_id {}".format(data_helper.validate_region_id(region_id)))
        print("validate_type_id {}".format(data_helper.validate_type_id(type_id)))
    # direct_market_functions.get_item_market_history_of_region()


def input_get_region_name():
    region_id = input("星域编号(10000001-10000069, 11000001-11000033, default: 10000002): ")
    region_id = '10000002' if region_id == '' else int(region_id)
    if data_helper.validate_region_id(region_id):
        print(data_helper.region_id_dict[region_id])
    else:
        print('invalid input')


def input_get_type_order_of_region():
    region_id = input("星域编号(10000001-10000069, 11000001-11000033, default: 10000002): ")
    region_id = 10000002 if region_id == '' else int(region_id)
    type_id = input("商品编号(default: 34): ")
    type_id = 34 if type_id == '' else int(type_id)
    if data_helper.validate_region_id(region_id):
        r = direct_market_api_functions.get_orders_of_region_single_thread(region_id, type_id=type_id)
        for i in r:
            print(i)
    else:
        print('invalid input')


def input_get_most_order_of_region():
    region_id = input("星域编号(10000001-10000069, 11000001-11000033, default: 10000002): ")
    region_id = 10000002 if region_id == '' else int(region_id)
    # time_n = input("时间范围(天): (default: 7)")
    # time_n = 7 if time_n == '' else int(time_n)
    top_n = input("获取前n个结果: (default: 10)")
    top_n = 10 if top_n == '' else int(top_n)
    thread_num = input("线程数: (default: 20)")
    thread_num = 20 if thread_num == '' else int(thread_num)
    if data_helper.validate_region_id(region_id):
        r = custom_functions.get_active_order_in_region_multi(region_id, thread_num)
        top_n = len(r) if len(r) < top_n else top_n
        for i in range(top_n):
            s, b = 0, 0
            for o in r[i][1]:
                if o['is_buy_order']:
                    b += 1
                else:
                    s += 1
            print("{} {} 总数: {} 买单: {} 卖单: {}".format(r[i][0], data_helper.type_id_dict[r[i][0]], len(r[i][1]), b, s))

    else:
        print('invalid input')


if __name__ == '__main__':
    input_get_most_order_of_region()
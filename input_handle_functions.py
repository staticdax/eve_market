#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import data_helper
import custom_functions
import direct_market_api_functions
import output_handle_functions
import test_functions


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
        r = custom_functions.get_active_order_in_region_multi_todo(region_id, thread_num)
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


def interstellar_logistic(region_id:int ,all_regions=False):
    if all_regions:
        need_update = str(input("是否更新全部星域订单?否则加载缓存或存档(Y/N)")).lower()
        if need_update == 'y' or need_update == 'yes':
            print("正在更新数据...")
            custom_functions.renew_region_markets_orders_dict_from_api_multi()
            custom_functions.renew_all_orders_by_typeid_dict()
            custom_functions.renew_all_profitable_orders_dict()
            print("数据更新完毕。")
        elif need_update == 't':
            data_helper.all_profitable_orders_dict = test_functions.fast_load_profitable_order_dict()
        else:
            print("不更新，正在载入...")
            # data_helper.all_profitable_orders_dict = test_functions.fast_load_profitable_order_dict()
            if len(data_helper.all_profitable_orders_dict) == 0:
                custom_functions.renew_all_orders_by_typeid_dict()
                custom_functions.renew_all_profitable_orders_dict()
    elif not all_regions:
        # 不用更新全部region的数据
        pass
    try:
        min_profit = input("设置最低利润: (default: 10,000,000)")
        min_profit = 10000000 if min_profit == '' else int(min_profit)
        ll = ['profit', 'buy_order_num', 'sell_order_num', 'volume', 'cost', 'profit_rate', 'rating']
        sorted_by = input("设置排序依据: (可选'profit', 'buy_order_num', 'sell_order_num', 'volume', 'cost', "
                          "'profit_rate', 'rating', default: rating)")
        sorted_by = 'rating' if sorted_by not in ll else str(sorted_by)
        if all_regions:
            data_helper.tmp_list = custom_functions.get_profitable_orders_sorted_dict(
                data_helper.all_profitable_orders_dict, min_profit=min_profit, sorted_by=sorted_by, reverse=True)
            output_handle_functions.interact_logistic_profitable_orders_dict(data_helper.tmp_list)
        else:
            pass
    except Exception as e:
        print(e)
        print("Exception: interstellar_logistic")


if __name__ == '__main__':
    interstellar_logistic(0, True)

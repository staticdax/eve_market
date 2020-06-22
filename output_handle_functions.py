#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import data_helper
from datetime import datetime, timedelta


def interact_logistic_profitable_orders_dict(profitable_orders_dict: dict):
    """
    处理profitable_orders_list列表的互动和显示

    :param profitable_orders_dict: 经过sorted的 data_helper.all_profitable_orders_list
        或 data_helper.region_profitable_orders_dict
        一般是custom_functions.get_profitable_orders_sorted_list()的输出
        形式为 {type_id_1: {'type_name': info, 'profit': info, ..., 'buy': [{order}, ...], 'sell': [{order}, ...]}, type_id_2: {...}, ...}

    :return:
    """
    p_dict = profitable_orders_dict
    dict_len = len(p_dict)
    page_cursor = 0
    page_line = 6

    if dict_len == 0 \
            or not isinstance(list(p_dict.values())[0], dict) \
            or 'rating' not in list(p_dict.values())[0].keys():
        print("Something wrong in orders_dict {}. Return".format(profitable_orders_dict))
        return

    p_list = list(p_dict.items()) # [(type_id,{info}), (type_id2, {info}), ...]
    while True:
        end_num = page_cursor + page_line
        end_num = end_num if dict_len > end_num else dict_len
        for page_num in range(page_cursor, end_num):
            type_id = p_list[page_num][0]
            tmp_dict = p_list[page_num][1]
            print("[{}/{}]{:>6d}\tprofit: {:>15,.1f}\tprofit_rate: {:>5.1f}\tvolume: {:<7,}\t"
                  "cost: {:>15,.2f}\tbuyer: {:>2d} seller: {:>2d} rating: {:<3.2f}\t{}"
                  .format(page_num+1, dict_len, type_id, tmp_dict['profit'], tmp_dict['profit_rate'],
                          tmp_dict['volume'], tmp_dict['cost'], len(tmp_dict['buy']), len(tmp_dict['sell']),
                          tmp_dict['rating'], tmp_dict['type_name']))
        il_choice_1 = input("(w:prev, z:next, g:top, G:end, [type_id]:select type_id, q:back):")
        if il_choice_1 == 'q':
            break
        elif il_choice_1 == 'w':
            page_cursor = 0 if page_cursor < page_line else page_cursor - page_line
        elif il_choice_1 == 'z' or il_choice_1 == '':
            page_cursor = dict_len - page_line if (page_cursor + page_line) > dict_len else page_cursor + page_line
            page_cursor = 0 if page_cursor < 0 else page_cursor
        elif il_choice_1 == 'G':
            page_cursor = dict_len - page_line
            page_cursor = 0 if page_cursor < 0 else page_cursor
        elif il_choice_1 == 'g':
            page_cursor = 0
        else:
            try:
                if int(il_choice_1) in p_dict:
                    tmp_dict = p_dict[int(il_choice_1)]
                    while True:
                        print("{}\tprofit: {:,}\tprofit_rate: {:>8.2f}\tcost: {:>15,.2f}\tbuyer: {:>2d}\tseller: {:>2d}\t{}"
                              .format(type_id, tmp_dict['profit'], tmp_dict['profit_rate'],
                                      tmp_dict['cost'], len(tmp_dict['buy']), len(tmp_dict['sell']),
                                      tmp_dict['type_name']))
                        print('''---------------------
a) 全部显示
b) 显示买单详情
s) 显示卖单详情
q) 返回
''')
                        il_choice_2 = input('其他任意键返回:')
                        if il_choice_2 == 'a':
                            interact_orders_dicts_list(tmp_dict['sell'],tmp_dict['buy'])
                            break
                            # print("WIP: interact_orders_dicts_list(tmp_dict['sell'],tmp_dict['buy'])")
                        elif il_choice_2 == 'b':
                            interact_orders_dicts_list(tmp_dict['buy'])
                        elif il_choice_2 == 's':
                            interact_orders_dicts_list(tmp_dict['sell'])
                        elif il_choice_2 == 'q':
                            break
                        else:
                            continue
            except ValueError as e:
                continue
            except Exception as e:
                print(e)
                print("Exception: il_choice_1 = input()")
        continue


def interact_orders_dicts_list(order_dicts_list: list, order_dicts_list_2=None):
    """
    处理订单字典组成的列表的交互和显示

    :param order_dicts_list: 订单字典组成的列表 [{order_1}, {order_2}, ...]
    :param order_dicts_list_2: 后备列表
    :return:
    """
    def display_order(order: dict, page_num: int, lst_len: int):
        location = data_helper.get_location_name(order['location_id'])
        system_id = order['system_id']
        order['range'] = 0 if order['range'] == 'station' else order['range']
        order['range'] = 99 if order['range'] == 'region' else order['range']
        if data_helper.validate_system_id(system_id):
            constellation_id = data_helper.system_constellation_dict[system_id]
            constellation = data_helper.get_constellation_name(constellation_id)
            region = data_helper.get_region_name(data_helper.constellation_region_dict[constellation_id])
            if not data_helper.validate_location_id(order['location_id']):
                location = "{} - {}".format(data_helper.get_system_name(system_id), location)
        else:
            constellation = "system_id:"
            region = system_id
        full_location = "[{}] < {} < {}".format(location, constellation, region)

        issue_time = datetime.strptime(order['issued'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=8)
        # UTC+8 datetime.timedelta(hours=8)
        duration = timedelta(order['duration'])
        due_time = issue_time + duration
        countdown = due_time - datetime.now()
        countdown = timedelta(days=countdown.days, seconds=countdown.seconds)

        # print("[{}/{}]\t数量: {:>7,} 价格: {:,} 范围: {:>2d} 最小成交量: {}\t距到期还有: {}\t位置: {}"
        #       .format(page_num + 1, list_len, order['volume_remain'], order['price'], order['range'],
        #               order['min_volume'], countdown, full_location))
        print("[{}/{}]\t数量: {:>7,} 价格: {} 范围: {:>2} 最小成交量: {}\t距到期还有: {}\t位置: {}"
              .format(page_num + 1, lst_len, order['volume_remain'], order['price'], order['range'],
                      order['min_volume'], countdown, full_location))

    for dct in order_dicts_list:
        if not isinstance(dct, dict):
            print("Something wrong writh order_dicts_list. Return.")
            return

    o_list = order_dicts_list
    type_id = o_list[0]['type_id']
    type_name = data_helper.get_type_name(type_id)
    list_len = len(order_dicts_list)
    page_line = 6
    cursor = 0

    if order_dicts_list_2 is not None:
        for dct in order_dicts_list_2:
            if not isinstance(dct, dict):
                print("Something wrong writh order_dicts_list_2. Return.")
                return
        o_list_2 = order_dicts_list_2
        print("{} {}".format(type_id, type_name))
        print('--------------------------------------卖单--------------------------------------')
        for num in reversed(range(len(o_list))):
            order = o_list[num]
            display_order(order, num, len(o_list))
        print('--------------------------------------买单--------------------------------------')
        for num in range(len(o_list_2)):
            order = o_list_2[num]
            display_order(order, num, len(o_list_2))
        print('-------------------------------------------------------------------------------')
        input()
        return

    while True:
        print("{} {}".format(type_id, type_name))
        end_num = cursor + page_line if (cursor + page_line) < list_len else list_len
        for num in range(cursor, end_num):
            order = o_list[num]
            display_order(order, num)

        io_choice_1 = input("(w:prev, z:next, g:top, G:end, q:back):")
        if io_choice_1 == 'q':
            return
        elif io_choice_1 == 'w':
            cursor = 0 if cursor < page_line else cursor - page_line
        elif io_choice_1 == 'z' or io_choice_1 == '':
            cursor = list_len - page_line if (cursor + page_line) > list_len else cursor + page_line
            cursor = 0 if cursor < 0 else cursor
        elif io_choice_1 == 'G':
            cursor = list_len - page_line
            cursor = 0 if cursor < 0 else cursor
        elif io_choice_1 == 'g':
            cursor = 0
        continue

#!/usr/bin/env python3

import data_helper
import route_calculator
from datetime import datetime, timedelta


def interact_logistic_profitable_orders_dict(profitable_orders_dict: dict):
    """
    处理profitable_orders_list列表的互动和显示

    :param profitable_orders_dict: 经过sorted的 data_helper.all_profitable_orders_list
        或 data_helper.region_profitable_orders_dict
        一般是custom_functions.get_profitable_orders_sorted_list()的输出
        形式为 {type_id_1: {'type_name': info, 'profit': info, ..., 'buy': [{order}, ...], 'sell': [{order}, ...]},
        type_id_2: {...}, ...}

    :return:
    """
    p_dict = profitable_orders_dict
    dict_len = len(p_dict)
    page_cursor = 0
    page_line = 15

    if dict_len == 0 \
            or not isinstance(list(p_dict.values())[0], dict) \
            or 'rating' not in list(p_dict.values())[0].keys():
        print("Something wrong with orders_dict {}. Return".format(profitable_orders_dict))
        return

    p_list = list(p_dict.items())  # [(type_id,{info}), (type_id2, {info}), ...]
    while True:
        end_num = page_cursor + page_line
        end_num = end_num if dict_len > end_num else dict_len
        for page_num in range(page_cursor, end_num):
            type_id = p_list[page_num][0]
            tmp_dict = p_list[page_num][1]
            # print("[{}/{}]{:>6d}\tprofit: {:>15,.1f}\tcost: {:>15,.2f}\tprofit_rate: {:>5.1f}\tquantity: {:<7,}\t"
            #       "buyer: {:>3d} seller: {:>3d} rating: {:<3.2f} TotalVol.: {:,.0f}\t{}"
            #       .format(page_num + 1, dict_len, type_id, tmp_dict['profit'], tmp_dict['cost'],
            #               tmp_dict['profit_rate'], tmp_dict['volume'], len(tmp_dict['buy']), len(tmp_dict['sell']),
            #               tmp_dict['rating'], tmp_dict['total_volume'], tmp_dict['type_name']))
            # rating这个东西好像显示的作用不大
            print("[{}/{}]{:>6d}\tprofit: {:>15,.1f}\tcost: {:>15,.2f}\tprofit_rate: {:>5.1f}\t"
                  "buyer: {:>3d} seller: {:>3d} qty.: {:<7,}\tTotalVol.: {:,.0f}\t{}"
                  .format(page_num + 1, dict_len, type_id, tmp_dict['profit'], tmp_dict['cost'],
                          tmp_dict['profit_rate'], len(tmp_dict['buy']), len(tmp_dict['sell']),
                          tmp_dict['volume'], tmp_dict['total_volume'], tmp_dict['type_name']))
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
                        print("{} {} profit_rate: {:.2f} profit: {:,.2f} cost: {:,.2f} buyer: {} "
                              "seller: {} qty.: {:,} volume: {:,} total_volume: {:,.2f}"
                              .format(int(il_choice_1), tmp_dict['type_name'],
                                      tmp_dict['profit_rate'], tmp_dict['profit'], tmp_dict['cost'],
                                      len(tmp_dict['buy']), len(tmp_dict['sell']), tmp_dict['volume'],
                                      data_helper.typeid_packaged_volume_dict[int(il_choice_1)],
                                      tmp_dict['total_volume']))
                        print('''---------------------
enter) 全部显示
b) 显示买单详情   
s) 显示卖单详情
q) 返回
''')
                        il_choice_2 = input('其他任意键返回:')
                        if il_choice_2 == '':
                            print("{} {} profit_rate: {:.2f} profit: {:,.2f} cost: {:,.2f} buyer: {} "
                                  "seller: {} qty.: {:,} volume: {:,} total_volume: {:,.2f}"
                                  .format(int(il_choice_1), tmp_dict['type_name'],
                                          tmp_dict['profit_rate'], tmp_dict['profit'], tmp_dict['cost'],
                                          len(tmp_dict['buy']), len(tmp_dict['sell']), tmp_dict['volume'],
                                          data_helper.typeid_packaged_volume_dict[int(il_choice_1)],
                                          tmp_dict['total_volume']))
                            interact_orders_dicts_list(tmp_dict['sell'], tmp_dict['buy'])
                            show_trade_route(int(il_choice_1))
                            # input()
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
            except ValueError:
                continue
            except Exception as e:
                print(e)
                print("Exception: il_choice_1 = input()")
        continue


def interact_orders_dicts_list(order_dicts_list: list, order_dicts_list_2=None):
    """
    处理订单字典组成的列表的交互和显示

    :param order_dicts_list: 订单字典组成的列表 [{order_1}, {order_2}, ...]
    :param order_dicts_list_2: 后备列表，存在第二个参数时，通常order_dicts_list为卖单列表，order_dicts_list_2为买单列表
    :return:
    """

    def display_order(order_dict: dict, page_num: int, lst_len: int):
        location = data_helper.get_location_name(order_dict['location_id'])
        system_id = order_dict['system_id']
        order_dict['range'] = 0 if order_dict['range'] == 'station' else order_dict['range']
        order_dict['range'] = 99 if order_dict['range'] == 'region' else order_dict['range']
        if data_helper.validate_system_id(system_id):
            constellation_id = data_helper.system_constellation_dict[system_id]
            constellation = data_helper.get_constellation_name(constellation_id)
            region = data_helper.get_region_name(data_helper.constellation_region_dict[constellation_id])
            if not data_helper.validate_location_id(order_dict['location_id']):
                location = "{} - {}".format(data_helper.get_system_name(system_id), location)
        else:
            constellation = "system_id:"
            region = system_id
        full_location = "[{}] < {} < {}".format(location, constellation, region)

        issue_time = datetime.strptime(order_dict['issued'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=8)
        # UTC+8 datetime.timedelta(hours=8)
        duration = timedelta(order_dict['duration'])
        due_time = issue_time + duration
        countdown = due_time - datetime.now()
        countdown = timedelta(days=countdown.days, seconds=countdown.seconds)

        # print("[{}/{}]\t数量: {:>7,} 价格: {:,} 范围: {:>2d} 最小成交量: {}\t距到期还有: {}\t位置: {}"
        #       .format(page_num + 1, list_len, order['volume_remain'], order['price'], order['range'],
        #               order['min_volume'], countdown, full_location))
        print("[{}/{}] 数量: {:<12,} 价格: {:,} 范围: {:>2} 最小成交量: {}\t距到期还有: {}\t位置: {}"
              .format(page_num + 1, lst_len, order_dict['volume_remain'], order_dict['price'], order_dict['range'],
                      order_dict['min_volume'], countdown, full_location))

    def scrolling_page(order_list: list):
        typeid = order_list[0]['type_id']
        typename = data_helper.get_type_name(typeid)
        list_len = len(order_list)
        page_line = 15
        cursor = 0
        while True:
            print("{} {}".format(typeid, typename))
            end_num = cursor + page_line if (cursor + page_line) < list_len else list_len
            for n in range(cursor, end_num):
                aorder = order_list[n]
                display_order(aorder, n, list_len)

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

    for dct in order_dicts_list:
        if not isinstance(dct, dict):
            print("Something wrong with order_dicts_list. Return.")
            return

    if order_dicts_list_2 is not None:
        o_list = order_dicts_list

        for dct in order_dicts_list_2:
            if not isinstance(dct, dict):
                print("Something wrong writh order_dicts_list_2. Return.")
                return

        o_list_2 = order_dicts_list_2
        if (len(o_list) + len(o_list_2)) < 50:
            print('--------------------------------------卖单--------------------------------------')
            for num in reversed(range(len(o_list))):
                order = o_list[num]
                display_order(order, num, len(o_list))
            print('--------------------------------------买单--------------------------------------')
            for num in range(len(o_list_2)):
                order = o_list_2[num]
                display_order(order, num, len(o_list_2))
            print('-------------------------------------------------------------------------------')
            return
        else:
            print('--------------------------------------卖单--------------------------------------')
            scrolling_page(o_list)
            print('--------------------------------------买单--------------------------------------')
            scrolling_page(o_list_2)
            print('-------------------------------------------------------------------------------')
        # input()
        return

    scrolling_page(order_dicts_list)


def show_trade_route(type_id: int):
    inp = input("显示贸易路线(Y/N)")
    inp = inp.lower()
    if inp != 'y' and inp != 'yes' and inp != '':
        return
    sec = input("安全路径优先？(Y/N)")
    sec = inp.lower()
    if sec == 'y' or sec == 'yes' or sec == '':
        min_security = 0.5
    else:
        min_security = 0.0
    while True:
        start_system_id = input("起始星域编号或名称(default: 吉他/30000142): ")
        start_system_id = 30000142 if start_system_id == '' else start_system_id
        try:
            start_system_id = int(start_system_id)
            if data_helper.validate_system_id(start_system_id):
                break
            else:
                print("Invalid input, try again.")
                continue
        except ValueError:  # start_system_id是非数字
            if data_helper.validate_system_name(start_system_id):
                f = filter(lambda x: x[1] == start_system_id, data_helper.system_id_dict.items())
                for k, v in f:
                    start_system_id = k
                break
            else:
                print("Invalid input, try again.")
                continue

        # if data_helper.validate_system_id(start_system_id) or data_helper.validate_system_name(start_system_id):
        #     if
    sell_orders_route, buy_orders_route, waypoints1, waypoints2 = route_calculator.trade_route_calc(start_system_id,
                                                                                                    type_id,
                                                                                                    min_security)
    print("Sell orders route: ", end='')
    route_calculator.show_route_info(sell_orders_route, waypoints1)
    print("Buy orders route: ", end='')
    route_calculator.show_route_info(buy_orders_route, waypoints2)

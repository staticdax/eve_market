#!/usr/bin/env python3

import data_helper
import custom_functions
import direct_api_functions
import output_handle_functions


def get_region_market_history():
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


def get_region_name():
    region_id = input("星域编号(10000001-10000069, 11000001-11000033, default: 10000002): ")
    region_id = '10000002' if region_id == '' else int(region_id)
    if data_helper.validate_region_id(region_id):
        print(data_helper.region_id_dict[region_id])
    else:
        print('invalid input')


def get_type_order_of_region():
    region_id = input("星域编号(10000001-10000069, 11000001-11000033, default: 10000002): ")
    region_id = 10000002 if region_id == '' else int(region_id)
    type_id = input("商品编号(default: 34): ")
    type_id = 34 if type_id == '' else int(type_id)
    type_name = data_helper.get_type_name_from_dict(type_id)
    if data_helper.validate_region_id(region_id):
        # r = direct_market_api_functions.get_orders_of_region_single_thread(region_id, type_id=type_id)
        # TODO: 单独更新这类订单，对比order_id，不存在的append，存在的对比volume_remain不一样的就更新
        r = dict()  # r是bns_orders_dict {'buy':[{order_1}, {order_2}, ...],'sell':[{}, {}, ...]}
        r['buy'] = list()
        r['sell'] = list()
        if len(data_helper.region_markets_orders_dict) == 0:
            r['buy'] = direct_api_functions.get_orders_of_region_single_thread(region_id, order_type='buy',
                                                                               type_id=type_id)
            r['sell'] = direct_api_functions.get_orders_of_region_single_thread(region_id, order_type='sell',
                                                                                type_id=type_id)
        else:
            for order in data_helper.region_markets_orders_dict[region_id]:
                if order['is_buy_order']:
                    r['buy'].append(order)
                else:
                    r['sell'].append(order)
        r['buy'].sort(key=lambda x: x['price'], reverse=True)  # 买单按价格降序排列，卖单价格按升序排列
        r['sell'].sort(key=lambda x: x['price'], reverse=False)
        print("{} {}".format(type_id, type_name))
        output_handle_functions.interact_orders_dicts_list(r['sell'], r['buy'])
    else:
        print('invalid input')


def get_most_order_of_region():
    print("[WIP]")
    return

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


def interstellar_logistic(region_id: int, regions='All'):
    if regions == 'All':
        need_update = str(input("是否更新全部星域订单?(Y/N)")).lower()
        if need_update == 'y' or need_update == 'yes' or need_update == '':
            print("正在更新数据...")
            custom_functions.renew_region_markets_orders_dict_multi()
            custom_functions.renew_all_orders_by_typeid_dict()
            custom_functions.renew_detailed_profitable_orders_dict()
            print("数据更新完毕。")
        elif need_update == 'test':
            data_helper.all_profitable_orders_dict = data_helper.fast_load_detailed_profitable_orders_dict()
        else:
            print("不更新，正在载入...")
            # data_helper.all_profitable_orders_dict = test_functions.fast_load_profitable_order_dict()
            if len(data_helper.detailed_profitable_orders_dict) == 0:
                custom_functions.renew_all_orders_by_typeid_dict()
                custom_functions.renew_detailed_profitable_orders_dict()
    elif regions == 'Empire regions':
        need_update = str(input("是否更新帝国区星域订单?(Y/N)")).lower()
        if need_update == 'y' or need_update == 'yes' or need_update == '':
            print("正在更新数据...")
            custom_functions.renew_region_markets_orders_dict_multi(region='Empire regions')
            custom_functions.renew_all_orders_by_typeid_dict()
            custom_functions.renew_detailed_profitable_orders_dict()
            print("数据更新完毕。")
        elif need_update == 'test':
            data_helper.all_profitable_orders_dict = data_helper.fast_load_detailed_profitable_orders_dict()
        else:
            print("不更新，正在载入...")
            # data_helper.all_profitable_orders_dict = test_functions.fast_load_profitable_order_dict()
            print("len(data_helper.all_profitable_orders_dict): {}".format(len(data_helper.detailed_profitable_orders_dict)))
            if len(data_helper.detailed_profitable_orders_dict) == 0:
                custom_functions.renew_all_orders_by_typeid_dict()
                custom_functions.renew_detailed_profitable_orders_dict()
    try:
        min_profit = input("设置最低利润: (default: 10,000,000)")
        min_profit = 10000000 if min_profit == '' else int(min_profit)
        choice_dict = {'p': 'profit', 'b': 'buy_order_num', 's': 'sell_order_num', 'q': 'volume', 'c': 'cost',
                       'pr': 'profit_rate', 'r': 'rating'}
        # 订单的数据结构中表示数量的volume在这里显示为quantity，实际上变量名依然为volume
        ll = ['profit', 'buy_order_num', 'sell_order_num', 'volume', 'cost', 'profit_rate', 'rating']
        sorted_by = input("设置排序依据: (可选[p]rofit, [b]uy_order_num, [s]ell_order_num, [q]uantity, [c]ost, "
                          "[pr]ofit_rate, [r]ating, default: rating)")
        if sorted_by not in choice_dict:
            sorted_by = 'volume' if sorted_by == 'quantity' else str(sorted_by) # 显示上的quantity转换为实际的变量名volume
            sorted_by = 'rating' if sorted_by not in ll else str(sorted_by)
        else:
            sorted_by = choice_dict[sorted_by]

        # 选择b, s, c, q 选项时应该在显示前将其正序排序
        if sorted_by in ['b', 's', 'c', 'q', 'buy_order_num', 'sell_order_num', 'cost', 'volume']:
            data_helper.tmp_dict = custom_functions.get_sorted_detailed_profitable_orders_dict(
                data_helper.detailed_profitable_orders_dict, min_profit=min_profit, sorted_by=sorted_by, reverse=False)
        else:
            data_helper.tmp_dict = custom_functions.get_sorted_detailed_profitable_orders_dict(
                data_helper.detailed_profitable_orders_dict, min_profit=min_profit, sorted_by=sorted_by, reverse=True)
        output_handle_functions.interact_logistic_profitable_orders_dict(data_helper.tmp_dict)
    except Exception as e:
        print(e)
        print("Exception: interstellar_logistic")


def get_region_id():
    while True:
        start_system_id = input("起始星域编号或名称(default: 吉他/30000142): ")
        start_system_id = 30000142 if start_system_id == '' else start_system_id
        try:
            start_system_id = int(start_system_id)
            if data_helper.validate_system_id(start_system_id):
                return start_system_id
                break
            else:
                print("Invalid input, try again.")
                continue
        except ValueError:  # start_system_id是非数字
            if data_helper.validate_system_name(start_system_id):
                f = filter(lambda x: x[1] == start_system_id, data_helper.system_id_dict.items())
                for k, v in f:
                    start_system_id = k
                return start_system_id
            else:
                print("Invalid input, try again.")
                continue
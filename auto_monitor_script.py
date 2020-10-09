#!/usr/bin/env python

import time
from datetime import datetime
import threading
import data_helper
import custom_functions
import output_handle_functions
import send_mail

data_helper.set_serenity_server()
# data_helper.set_tranquility_server()
# anno for git
min_profit = 10000000
sorted_by = 'profit'

exclusive_name_list = ['三钛合金', '锶包合物', '电子元件', '长肢龙鹿的卵', '希莫非特', '液化臭氧', '乳制品', '抗生素', '全息记忆盘',
                       '幽灵饮料', '类晶体胶矿', '氢电池', '同位聚合体', '土壤', '盐酸', '崴砣柯', '重水', '药草', '冷藏食品', '小麦',
                       '酷菲', '蛋白食物', '凡晶石', '垃圾', '香料汽水', '蓝色斜长岩', '库马克', '数据单', '灼烧岩', '碳', '富斜长岩',
                       '斜长岩', '浓缩灼烧岩', '报告', '富凡晶石', '干焦岩', '类银超金属', '超新星诺克石', '超噬矿', '晶状石英核岩',
                       '富沸石', '发光水硼砂']
exclusive_id_list = []
oneb_set = set()

for n in exclusive_name_list:
    i = data_helper.get_type_id(n)
    if i != -1:
        exclusive_id_list.append(i)


class MyPollingThread(threading.Thread):
    def __init__(self, sleep_time):
        threading.Thread.__init__(self)
        self.sleep_time = sleep_time
        self.setDaemon(True)

    def run(self) -> None:
        polling_orders(self.sleep_time)


def polling_orders(sleep_time: int):
    while True:
        custom_functions.renew_region_markets_orders_dict_multi(region='Empire regions')
        # custom_functions.renew_region_markets_orders_dict_multi(region='All')
        custom_functions.renew_all_orders_by_typeid_dict()
        custom_functions.renew_detailed_profitable_orders_dict()
        # data_helper.all_profitable_orders_dict = data_helper.fast_load_detailed_profitable_orders_dict()

        data_helper.tmp_dict = custom_functions.get_sorted_detailed_profitable_orders_dict(
            data_helper.detailed_profitable_orders_dict, min_profit=min_profit, sorted_by=sorted_by, reverse=True)

        for ek in exclusive_id_list:
            if ek in data_helper.tmp_dict.keys():
                data_helper.tmp_dict.pop(ek)

        print_my_tmp_dict()

        need_send_mail = check_oneb_trade()
        if need_send_mail:
            send_oneb_mail()

        time.sleep(sleep_time)


def print_my_tmp_dict():
    now = datetime.now()
    print("---------------------------- {}{}{:02d} - {:02d}:{:02d}:{:02d} ----------------------------".format(now.year,
                                                                                                               now.month,
                                                                                                               now.day,
                                                                                                               now.hour,
                                                                                                               now.minute,
                                                                                                               now.second))
    for item in data_helper.tmp_dict.items():
        type_id = item[0]
        type_dict = item[1]
        print("{}\tprofit: {:>15,.1f}\tcost: {:>15,.2f}\tprofit_rate: {:>5.1f}\t"
              "buyer: {:>3d} seller: {:>3d} qty.: {:<7,}\tTotalVol.: {:,.0f}\t{}"
              .format(type_id, type_dict['profit'], type_dict['cost'],
                      type_dict['profit_rate'], len(type_dict['buy']), len(type_dict['sell']),
                      type_dict['volume'], type_dict['total_volume'], type_dict['type_name']))
        # print("{} {}".format(type_id, type_dict['type_name']))


def get_order_info():
    while True:
        type_id = input()
        try:
            type_id = int(type_id)
        except ValueError:
            print('Please input type id.')
            continue
        if not data_helper.validate_type_id(type_id) or type_id not in data_helper.tmp_dict.keys():
            print('Type id not in orders.')
            continue
        t_dict = data_helper.tmp_dict[type_id]
        print("{} {} profit_rate: {:.2f} profit: {:,.2f} cost: {:,.2f} buyer: {} "
              "seller: {} qty.: {:,} volume: {:,} total_volume: {:,.2f}"
              .format(type_id, t_dict['type_name'],
                      t_dict['profit_rate'], t_dict['profit'], t_dict['cost'],
                      len(t_dict['buy']), len(t_dict['sell']), t_dict['volume'],
                      data_helper.typeid_packaged_volume_dict[type_id],
                      t_dict['total_volume']))
        output_handle_functions.interact_orders_dicts_list(t_dict['sell'], t_dict['buy'])
        output_handle_functions.show_trade_route(int(type_id))
        print_my_tmp_dict()


def check_oneb_trade():
    """

    :return: true, oneb_tmp_set发生改变; false, oneb_tmp_set未改名或为oneb_set的子集
    """
    global oneb_set
    oneb = 300000000
    oneb_tmp_set = set()
    oneb_order_iter = filter(lambda x: x[1]['profit'] >= oneb, data_helper.tmp_dict.items())
    for item in oneb_order_iter:
        oneb_tmp_set.add(item[0])
    if len(oneb_tmp_set) == 0:
        oneb_set = oneb_tmp_set
        return False
    if oneb_tmp_set != oneb_set:
        if oneb_tmp_set.issubset(oneb_set):
            return False
        oneb_set = oneb_tmp_set
        return True
    else:
        return False


def send_oneb_mail():
    mail_msg = ''
    for i in oneb_set:
        t_dict = data_helper.tmp_dict[i]
        mail_msg += "{} {} profit_rate: {:.2f} profit: {:,.2f} cost: {:,.2f} qty.: {:,} volume: {:,} " \
                    "total_volume: {:,.2f} \n".format(i, t_dict['type_name'], t_dict['profit_rate'],
                                                      t_dict['profit'], t_dict['cost'], t_dict['volume'],
                                                      data_helper.typeid_packaged_volume_dict[i],
                                                      t_dict['total_volume'])
    send_mail.send(mail_msg)


def main():
    polling_thread = MyPollingThread(300)
    polling_thread.start()

    get_order_info()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import data_helper
import input_handle_functions
import direct_api_functions


class Menu:
    def __init__(self, title):
        self.title = title


class ServerMenu(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)
        self.mainMenu = MainMenu("Welcome to EVE Online Swagger tool.")

    def run(self):
        while True:
            print(self.title)
            print(
                '''选择服务器
---------------------
s) 晨曦
t) Tranquility
q) exit
---------------------''')
            choice = input("select: ")
            if choice == 's' or choice == 't':
                if choice == 's':
                    direct_api_functions.set_serenity_server()
                    data_helper.set_serenity_server()
                elif choice == 't':
                    direct_api_functions.set_tranquility_server()
                    data_helper.set_tranquility_server()
                self.mainMenu.run()
            elif choice == 'q':
                break
            else:
                input('Invalid input.')
                continue

class MainMenu(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)
        self.menu_a = MenuA("常用功能")
        self.menu_b = MenuB("资料查询")

    def run(self):
        while True:
            print(self.title)
            print(
                '''---------------------
a) 常用功能
b) 资料查询
q) back
---------------------''')
            choice = input("select: ")
            if choice == 'a':
                self.menu_a.run()
            elif choice == 'b':
                self.menu_b.run()
            elif choice == 'q':
                break
            else:
                input('Invalid input.')
                continue
            # input('press any key to continue...')


class MenuA(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)
        self.menu_interstellar = MenuInterstellarLogistic("欢迎来到 星际物流 Inc.")

    def run(self):
        while True:
            print(self.title)
            print(
                '''---------------------
h) 获取指定商品在星域市场历史数据
m) 获取星域市场n天内订单最多的商品
n) 获取星域市场此时订单最多的商品(todo:重写)
t) 获取星域市场中指定商品订单
l) 星际物流模式
q) back
---------------------''')
            choice = input("select: ")
            if choice == 'h':
                input_handle_functions.get_region_market_history()
            elif choice == 't':
                input_handle_functions.get_type_order_of_region()
            elif choice == 'n':
                print("(todo:重写)")
                # input_handle_functions.get_most_order_of_region()
            elif choice == 'l':
                self.menu_interstellar.run()
            elif choice == 'q':
                break
            else:
                input('Invalid input.')
                continue
            # input('press enter to continue...')


class MenuB(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)

    def run(self):
        while True:
            print(self.title)
            print(
                '''---------------------
r) 查询星域名称
b) option 2
q) back
---------------------''')
            choice = input("select: ")
            if choice == 'r':
                input_handle_functions.get_region_name()
            elif choice == 'b':
                print("option 2")
            elif choice == 'q':
                break
            else:
                input('Invalid input.')
                continue
            # input('press enter to continue...')


class MenuInterstellarLogistic(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)

    def run(self):
        while True:
            print(self.title)
            print(
                '''---------------------
r) 全星域范围
s) 帝国区星域范围
q) back
---------------------''')
            choice = input("select: ")
            if choice == 's':
                # print("WIP:...")
                input_handle_functions.interstellar_logistic(0, regions='Empire regions')
            elif choice == 'r':
                input_handle_functions.interstellar_logistic(0, regions='All')
            elif choice == 'q':
                break
            else:
                input('Invalid input.Press enter to continue...')
                continue
            # input('press enter to continue...')


def main():
    menu = ServerMenu("Welcome to EVE Online Swagger tool.")
    menu.run()
    # data_helper.rewrite_type_id_json_file()


if __name__ == '__main__':
    main()

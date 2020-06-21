#!/usr/bin/enb python3
# -*- encoding:UTF-8 -*-


import direct_market_api_functions
import data_helper
import time
import input_handle_functions


class Menu:
    def __init__(self, title):
        self.title = title


class MainMenu(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)
        self.menua = MenuA("常用功能")
        self.menub = MenuB("固定资料查询")

    def run(self):
        while True:
            print("\033c")
            print(self.title)
            print('''
---------------------
a) 常用功能
b) 固定资料查询
x) exit
---------------------''')
            choice = input("select: ")
            if choice == 'a':
                self.menua.run()
            elif choice == 'b':
                self.menub.run()
            elif choice == 'x':
                break
            else:
                input('Invalid input.')
                continue
            input('press any key to continue...')


class MenuA(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)

    def run(self):
        while True:
            print("\033c")
            print(self.title)
            print('''
---------------------
h) 获取指定商品在星域市场历史数据
t) 获取星域市场中指定商品订单
n) 获取星域市场此时订单最多的商品
m) 获取星域市场n天内订单最多的商品
x) back
---------------------''')
            choice = input("select: ")
            if choice == 'h':
                input_handle_functions.input_get_region_market_history()
            elif choice == 't':
                input_handle_functions.input_get_type_order_of_region()
            elif choice == 'n':
                input_handle_functions.input_get_most_order_of_region()
            elif choice == 'x':
                break
            else:
                input('Invalid input.')
                continue
            input('press any key to continue...')


class MenuB(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)

    def run(self):
        while True:
            print("\033c")
            print(self.title)
            print('''
---------------------
r) 查询星域名称
b) option 2
x) back
---------------------''')
            choice = input("select: ")
            if choice == 'r':
                input_handle_functions.input_get_region_name()
            elif choice == 'b':
                print("option 2")
            elif choice == 'x':
                break
            else:
                input('Invalid input.')
                continue
            input('press any key to continue...')



def main():
    menu = MainMenu("Welcome to EVE Online Swagger tool.")
    menu.run()
    data_helper.rewrite_type_id_json_file()

if __name__ == '__main__':
    main()

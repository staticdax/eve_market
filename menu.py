#!/usr/bin/enb python3
# -*- encoding:UTF-8 -*-


import direct_market_functions
import data_helper
import time


class Menu:
    def __init__(self, title):
        self.title = title


class MainMenu(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)
        self.menua = MenuA("常用功能")

    def run(self):
        while True:
            print(self.title)
            print('''
---------------------
a) 常用功能
b) option b
x) exit
---------------------''')
            choice = input("select: ")
            if choice == 'a':
                self.menua.run()
            elif choice == 'b':
                pass
            elif choice == 'x':
                break
            else:
                print('Invalid input.')
                continue


class MenuA(Menu):
    def __init__(self, title):
        Menu.__init__(self, title)

    def run(self):
        while True:
            print(self.title)
            print('''
---------------------
h) 获取指定商品在星域市场历史数据
b) option 2
x) back
---------------------''')
            choice = input("select: ")
            if choice == 'h':
                input_get_region_market_history()
            elif choice == 'b':
                print("option 2")
            elif choice == 'x':
                break
            else:
                print('Invalid input.')
                continue


def input_get_region_market_history():
    region_id = input("星域编号(default: 10000002): ")
    region_id = 10000002 if region_id == '' else region_id
    print(region_id)
    type_id = input("商品编号(default: 34): ")
    type_id = 34 if type_id == '' else type_id
    print(type_id)
    if data_helper.validate_region_id(region_id) and data_helper.validate_type_id(type_id):
        print("星域编号: {} 商品编号: {}".format(region_id, type_id))
        r = direct_market_functions.get_region_market_history(region_id, type_id)
        for i in r:
            print(i)
    else:
        print('invalid input')
        print("validate_region_id {}".format(data_helper.validate_region_id(region_id)))
        print("validate_type_id {}".format(data_helper.validate_type_id(type_id)))
    # direct_market_functions.get_region_market_history()


def main():
    menu = MainMenu("This is main menu.")
    menu.run()


if __name__ == '__main__':
    main()

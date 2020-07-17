#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-

import json
import direct_market_api_functions
import threading
import time
import requests
import gc

def fast_load_profitable_order_dict():
    with open('data/test/all_profitable_orders_dict.json') as f:
        j =  json.load(f)

    r = dict()
    for type_id, info in j.items():
        r[int(type_id)] = info

    return r

class TestClass:
    def __init__(self, content):
        self.content = content

    def add_content(self, c2):
        if isinstance(c2, list):
            self.content += c2
        if isinstance(c2, str):
            self.content += [c2]


class TestThread(threading.Thread):
    def __init__(self, tc: TestClass):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.tc = tc

    def run(self) -> None:
        # r = direct_market_api_functions.get_orders_of_region_one_page_raw_response(10000002, page=1)
        # # jj = r.json()
        # # self.tc.add_content(jj)
        # self.tc.add_content(r.text)
        self.tc.add_content('M'*1024)


def test():

    while True:
        c = ["hello", "world"]
        tc = TestClass(c)


        t_n = 10
        threads = [TestThread(tc) for i in range(t_n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # for _ in range(t_n):
        #     r = direct_market_api_functions.get_orders_of_region_one_page_raw_response(10000002, page=1)
        #     tc.add_content(r.json())

        choice = input("stop(y/n)")
        if choice.lower() == 'y':
            break
        else:
            continue


if __name__ == '__main__':
    test()
#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-


import direct_market_functions
import threading
import queue
import json
import data_helper


thread_num = 20
threadLock = threading.Lock()


class MyGetSumTask:
    def __init__(self, region_id: int, type_id_list: list, duration: int):
        self.region_id = region_id
        # self.type_id_list = type_id_list
        self.q = queue.Queue()
        threadLock.acquire()
        for i in type_id_list:
            self.q.put(i)
        threadLock.release()

        self.duration = duration
        self.result_dict = dict()


class MyGetVolumeSumThread(threading.Thread):
    def __init__(self, my_get_sum_task: MyGetSumTask, num: int):
        threading.Thread.__init__(self)
        self.task = my_get_sum_task
        self.num = num

    def run(self) -> None:
        get_last_n_day_volume_single_thread(self.task)


def get_last_n_day_volume_single_thread(task: MyGetSumTask):
    while not task.q.empty():
        threadLock.acquire()
        if not task.q.empty():
            type_id = task.q.get()
            print("\rTask queue size: {}".format(task.q.qsize()), end="")
            threadLock.release()
            try:
                task.result_dict[type_id] = direct_market_functions.get_last_n_day_volume(task.region_id, type_id, task.duration)
            except Exception as e:
                print(e)
                threadLock.acquire()
                task.q.put(type_id)
                threadLock.release()
        else:
            threadLock.release()
        # time.sleep(0.5)


class MyGetOrderSumThread(threading.Thread):
    def __init__(self, my_get_sum_task: MyGetSumTask, num: int):
        threading.Thread.__init__(self)
        self.task = my_get_sum_task
        self.num = num

    def run(self) -> None:
        get_last_n_day_orders_single_thread(self.task)


def get_last_n_day_orders_single_thread(task: MyGetSumTask):
    while not task.q.empty():
        threadLock.acquire()
        if not task.q.empty():
            type_id = task.q.get()
            print("\rTask queue size: {}".format(task.q.qsize()), end="")
            threadLock.release()
            try:
                task.result_dict[type_id] = direct_market_functions.get_last_n_day_orders(task.region_id, type_id, task.duration)
            except Exception as e:
                print(e)
                threadLock.acquire()
                task.q.put(type_id)
                threadLock.release()
        else:
            threadLock.release()


def test_sample():
    # region_id = 10000002
    region_id = 10000011
    type_id_list = direct_market_functions.get_type_ids_have_active_order_in_region(region_id)
    print(type_id_list)
    duration = 7
    my_task = MyGetSumTask(region_id, type_id_list, duration)
    # threads = [MyGetVolumeSumThread(my_task, i) for i in range(thread_num)]
    threads = [MyGetOrderSumThread(my_task, i) for i in range(thread_num)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    with open('./get_sum_result.txt', 'w') as f:
        json.dump(my_task.result_dict, f)


def test_sample2():
    with open('./get_sum_result.txt', 'r') as f:
        order_sum = json.load(f)

    type_id_dict = data_helper.load_type_id()
    max_order_count = max(list(order_sum.values()))
    max_order_type_id = [k for (k, v) in order_sum.items() if v == max_order_count]
    for i in max_order_type_id:
        print("{} {} max order count: {:,}".format(i, type_id_dict[str(i)], max_order_count))


if __name__ == '__main__':
    test_sample()
    test_sample2()

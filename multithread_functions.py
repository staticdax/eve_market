#!/usr/bin/env python3

import threading
import queue
import data_helper
import direct_market_api_functions

thread_num = 20
threadLock = threading.Lock()


class MyGetTask:
    """
    一个通用的的任务类

    self.region_id
    self.lock 线程锁
    self.q 任务队列，存放任务变量的列表的元素初始化时将依次入队
    self.result_dict 结果字典变量，元素形式自定义
    """

    def __init__(self, task_list: list, region_id=10000001):
        self.region_id = region_id
        self.lock = threading.Lock()
        self.q = queue.Queue()
        self.lock.acquire()
        for i in task_list:
            self.q.put(i)
        self.lock.release()
        self.result_dict = dict()


class MyGetCurrentOrderInRegionThread(threading.Thread):
    def __init__(self, my_get_task: MyGetTask, num=0):
        threading.Thread.__init__(self)
        self.task = my_get_task
        self.num = num

    def run(self) -> None:
        get_current_order_of_type_in_region_single(self.task)


def get_current_order_of_type_in_region_single(task: MyGetTask):
    while not task.q.empty():
        task.lock.acquire()
        if not task.q.empty():
            type_id = task.q.get()
            print("\rTask queue size: {}    ".format(task.q.qsize()), end="")
            task.lock.release()
            try:
                r = direct_market_api_functions.get_orders_of_region_single_thread(task.region_id, type_id=type_id)
                if len(r) > 0:
                    task.result_dict[type_id] = r
            except Exception as e:
                print("{} position: {}".format(e, "get_current_order_of_type_in_region_single"))
                task.lock.acquire()
                task.q.put(type_id)
                task.lock.release()
        else:
            task.lock.release()


class MyGetOrdersOfAllRegionsThread(threading.Thread):
    def __init__(self, task: MyGetTask):
        threading.Thread.__init__(self)
        self.task = task
        self.setDaemon(True)

    def run(self) -> None:
        get_orders_of_all_regions_from_api_single(self.task)
        pass


def get_orders_of_all_regions_from_api_single(task: MyGetTask):
    while not task.q.empty():
        task.lock.acquire()
        if not task.q.empty():
            region_id = task.q.get()
            print("\rGet All Orders Task queue size: {}    ".format(task.q.qsize()), end="")
            task.lock.release()
            try:
                r_response = direct_market_api_functions.get_orders_of_region_one_page_raw_response(region_id)
                if r_response.status_code == 200:
                    x_pages = int(r_response.headers['X-Pages'])
                    if x_pages == 1:
                        task.result_dict[region_id] = r_response.json()
                    elif 1 < x_pages < 20:
                        task.result_dict[region_id] = direct_market_api_functions.get_orders_of_region_single_thread(
                            region_id)
                    elif x_pages >= 20:
                        # page_list = [i for i in range(1,x_pages+1)]
                        # print(x_pages)
                        page_list = range(1, x_pages + 1)
                        get_page_sub_task = MyGetTask(page_list, region_id=region_id)
                        t_num = 10
                        # t_num = 1
                        threads = [GetOrdersOfRegionOnePageThread(get_page_sub_task) for i in range(t_num)]
                        for t in threads:
                            t.start()
                        for t in threads:
                            t.join()
                        # print(get_page_sub_task.result_dict[region_id])
                        task.result_dict[region_id] = get_page_sub_task.result_dict[region_id]
                        # del threads
                    else:
                        raise Exception(
                            "something wrong with request {} orders error, response: {}".format(region_id, r_response))
                else:
                    raise Exception("request {} orders error, status_code: {}".format(region_id, r_response.status_code))
            except Exception as e:
                print(e)
                task.q.put(region_id)
                # with task.lock:
                #     task.q.put(region_id)
        else:
            task.lock.release()


class GetOrdersOfRegionOnePageThread(threading.Thread):
    def __init__(self, task: MyGetTask):
        threading.Thread.__init__(self)
        self.task = task
        self.setDaemon(True)

    def run(self) -> None:
        while not self.task.q.empty():
            self.task.lock.acquire()
            if not self.task.q.empty():
                page = self.task.q.get()
                print("\rregion: {} Task queue size: {}    ".format(self.task.region_id, self.task.q.qsize()), end='')
                self.task.lock.release()
                try:
                    r = direct_market_api_functions.get_orders_of_region_one_page_raw_response(self.task.region_id,
                                                                                               page=page)
                    if r.status_code == 200:
                        if self.task.region_id not in self.task.result_dict.keys():
                            self.task.result_dict[self.task.region_id] = list()
                        self.task.result_dict[self.task.region_id] += r.json()
                        # del r
                    else:
                        raise Exception("request {} orders error: {} page: {}".format(self.task.region_id, r, page))
                except Exception as e:
                    print("{} position: GetOrdersOfRegionOnPageThread {}".format(e, self.name))
                    self.task.lock.acquire()
                    self.task.q.put(page)
                    self.task.lock.release()
            else:
                self.task.lock.release()


if __name__ == '__main__':
    # test_sample()
    # test_sample2()
    # test_sample3()
    # test_sample4()
    pass

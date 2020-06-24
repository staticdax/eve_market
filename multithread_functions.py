#!/usr/bin/env python3
# -*- encoding:UTF-8 -*-
import custom_functions
import direct_market_api_functions
import threading
import queue
import data_helper

thread_num = 20
threadLock = threading.Lock()


class MyGetHistoryTask:
    def __init__(self, region_id, type_id_list: list):
        self.region_id = region_id
        self.q = queue.Queue()
        threadLock.acquire()
        for i in type_id_list:
            self.q.put(i)
        threadLock.release()


class MyGetHistoryThread(threading.Thread):
    def __init__(self, my_get_history_task: MyGetHistoryTask, num=0):
        threading.Thread.__init__(self)
        self.task = my_get_history_task
        self.num = num

    def run(self) -> None:
        get_item_market_history_of_region_single_thread(self.task)


def get_item_market_history_of_region_single_thread(task: MyGetHistoryTask):
    while not task.q.empty():
        threadLock.acquire()
        if not task.q.empty():
            type_id = task.q.get()
            print("\rTask queue size: {}".format(task.q.qsize()), end="")
            threadLock.release()
            try:
                custom_functions.get_item_market_history_of_region_from_api_or_local(task.region_id, type_id)
            except Exception as e:
                print(e)
                threadLock.acquire()
                task.q.put(type_id)
                threadLock.release()
        else:
            threadLock.release()


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
            print("\rTask queue size: {}".format(task.q.qsize()), end="")
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
            print("\rGet All Orders Task queue size: {}".format(task.q.qsize()), end="")
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
                with task.lock:
                    task.q.put(region_id)
                # task.lock.acquire()
                # task.q.put(region_id)
                # task.lock.release()
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
                print("\rregion: {} Task queue size: {}".format(self.task.region_id, self.task.q.qsize()), end='')
                self.task.lock.release()
                try:
                    r = direct_market_api_functions.get_orders_of_region_one_page_raw_response(self.task.region_id,
                                                                                               page=page)
                    if r.status_code == 200:
                        if self.task.region_id not in self.task.result_dict.keys():
                            self.task.result_dict[self.task.region_id] = list()
                        self.task.result_dict[self.task.region_id] += r.json()
                    else:
                        raise Exception("request {} orders error: {} page: {}".format(self.task.region_id, r, page))
                except Exception as e:
                    print("{} position: GetOrdersOfRegionOnPageThread {}".format(e, self.name))
                    self.task.lock.acquire()
                    self.task.q.put(page)
                    self.task.lock.release()
            else:
                self.task.lock.release()


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
    def __init__(self, my_get_sum_task: MyGetSumTask, num=0):
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
                task.result_dict[type_id] = custom_functions.get_last_n_day_volume(task.region_id, type_id,
                                                                                   task.duration)
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
                task.result_dict[type_id] = custom_functions.get_last_n_day_orders(task.region_id, type_id,
                                                                                   task.duration)
            except Exception as e:
                print(e)
                threadLock.acquire()
                task.q.put(type_id)
                threadLock.release()
        else:
            threadLock.release()


class WriteJsonIntoFileThread(threading.Thread):
    def __init__(self, file_path: str, file_name: str, content: list):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.file_name = file_name
        self.content = content

    def run(self) -> None:
        data_helper.write_json_into_file(self.file_path, self.file_name, self.content)


def write_json_into_file_multi_thread(file_path: str, file_name: str, content: list):
    try:
        # _thread.start_new_thread(data_helper.write_json_into_file, (file_path, file_name, content, ))
        t = WriteJsonIntoFileThread(file_path, file_name, content)
        t.start()
    except Exception as e:
        print(e)
        print('Exception: write_json_into_file_multi_thread')


# region_id = 10000002
# region_id = 10000011
# regionid = 10000064

# def test_sample():
#     type_id_list = direct_market_api_functions.get_type_ids_have_active_order_in_region(regionid)
#     print(type_id_list)
#     duration = 7
#     my_task = MyGetSumTask(regionid, type_id_list, duration)
#     # threads = [MyGetVolumeSumThread(my_task, i) for i in range(thread_num)]
#     threads = [MyGetOrderSumThread(my_task, i) for i in range(thread_num)]
#     for t in threads:
#         t.start()
#
#     for t in threads:
#         t.join()
#
#     # with open('./get_sum_result.txt', 'w') as f:
#     #     json.dump(my_task.result_dict, f)
#     max_order_sorted = sorted(my_task.result_dict.items(), key=lambda x:x[1], reverse=True)
#     for i in range(5):
#         type_id = str(max_order_sorted[i][0])
#         print("{} {} {}".format(type_id, data_helper.type_id_dict[type_id], max_order_sorted[i]))
#
#
# def test_sample2():
#     with open('./get_sum_result.txt', 'r') as f:
#         order_sum = json.load(f)
#
#     max_order_count = max(list(order_sum.values()))
#     max_order_type_id = [k for (k, v) in order_sum.items() if v == max_order_count]
#     for i in max_order_type_id:
#         print("{} {} max order count: {:,}".format(i, data_helper.type_id_dict[i], max_order_count))
#
#
# def test_sample3():
#     type_id_list = direct_market_api_functions.get_type_ids_have_active_order_in_region(regionid)
#     print(type_id_list)
#     my_task = MyGetHistoryTask(regionid, type_id_list)
#     threads = [MyGetHistoryThread(my_task, i) for i in range(thread_num)]
#     for t in threads:
#         t.start()
#
# def test_sample4():
#     type_id_list = direct_market_api_functions.get_type_ids_have_active_order_in_region(regionid)
#     print(type_id_list)
#     my_task = MyGetTask(type_id_list, regionid)
#     threads = [MyGetCurrentOrderInRegionThread(my_task, i) for i in range(thread_num)]
#     for t in threads:
#         t.start()


if __name__ == '__main__':
    # test_sample()
    # test_sample2()
    # test_sample3()
    # test_sample4()
    pass

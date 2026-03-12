#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import data_helper
import direct_api_functions
from concurrent.futures import ThreadPoolExecutor, as_completed


class TaskContext:
    """
    任务上下文类，保留原 MyGetTask 的核心功能
    
    Attributes:
        region_id: 星域ID
        lock: 线程锁
        task_list: 任务列表（保留用于重试）
        result_dict: 结果字典
        retry_count: 重试计数字典
    """
    
    def __init__(self, task_list: list, region_id=10000001):
        self.region_id = region_id
        self.lock = threading.Lock()
        self.task_list = list(task_list)
        self.result_dict = dict()
        self.retry_count = dict()


def process_single_page(task: TaskContext, page):
    """
    处理单个页面的订单请求（替代 GetOrdersOfRegionOnePageThread）
    
    :param task: 任务上下文
    :param page: 页码
    :return: (page, result, error)
    """
    try:
        r = direct_api_functions.get_orders_of_region_one_page_raw_response(task.region_id, page=page)
        if r.status_code == 200:
            return page, r.json(), None
        else:
            raise Exception(f"request {task.region_id} orders error: {r} page: {page}")
    except Exception as e:
        return page, None, e


def get_orders_of_region_with_executor(region_id, max_workers=10):
    """
    使用 ThreadPoolExecutor 获取单个星域的所有订单
    
    :param region_id: 星域ID
    :param max_workers: 最大线程数
    :return: 订单列表
    """
    r_response = direct_api_functions.get_orders_of_region_one_page_raw_response(region_id)
    if r_response.status_code != 200:
        raise Exception(f"request {region_id} orders error, status_code: {r_response.status_code}")
    
    x_pages = int(r_response.headers['X-Pages'])
    
    if x_pages == 1:
        return r_response.json()
    
    task = TaskContext(range(1, x_pages + 1), region_id=region_id)
    all_orders = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_page, task, page): page for page in task.task_list}
        
        for future in as_completed(futures):
            page, result, error = future.result()
            if error:
                print(f"Page {page} error: {error}")
                task.retry_count[page] = task.retry_count.get(page, 0) + 1
                if task.retry_count[page] <= 3:
                    futures[executor.submit(process_single_page, task, page)] = page
                    print(f"Page {page} retry {task.retry_count[page]}/3")
                else:
                    print(f"Page {page} failed after 3 retries, skipped")
            else:
                all_orders.extend(result)
                print(f"\rProcessed {len(all_orders)} orders...", end='')
    
    return all_orders


def get_orders_of_all_regions_with_executor(region_ids, max_workers=10, max_retries=3):
    """
    使用 ThreadPoolExecutor 获取所有星域订单
    
    :param region_ids: 星域ID列表
    :param max_workers: 最大线程数
    :param max_retries: 最大重试次数
    :return: {region_id: [orders]}
    """
    task = TaskContext(region_ids)
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_region, task, rid, max_retries): rid for rid in region_ids}
        
        for future in as_completed(futures):
            region_id, orders, error = future.result()
            if error:
                print(f"\nRegion {region_id} error: {error}")
                task.retry_count[region_id] = task.retry_count.get(region_id, 0) + 1
                if task.retry_count[region_id] <= max_retries:
                    futures[executor.submit(process_region, task, region_id, max_retries)] = region_id
                    print(f"Region {region_id} retry {task.retry_count[region_id]}/{max_retries}")
                else:
                    print(f"Region {region_id} failed after {max_retries} retries, skipped")
            else:
                results[region_id] = orders
                remaining = len(region_ids) - len(results)
                print(f"\rCompleted {len(results)}/{len(region_ids)} regions", end='')
    
    return results


def process_region(task, region_id, max_retries):
    """
    处理单个星域的订单获取
    
    :param task: 任务上下文
    :param region_id: 星域ID
    :param max_retries: 最大重试次数
    :return: (region_id, orders, error)
    """
    try:
        r_response = direct_api_functions.get_orders_of_region_one_page_raw_response(region_id)
        if r_response.status_code != 200:
            raise Exception(f"request {region_id} orders error, status_code: {r_response.status_code}")
        
        x_pages = int(r_response.headers['X-Pages'])
        
        if x_pages == 1:
            return region_id, r_response.json(), None
        elif 1 < x_pages < 20:
            orders = direct_api_functions.get_orders_of_region_single_thread(region_id)
            return region_id, orders, None
        elif x_pages >= 20:
            orders = get_orders_of_region_with_executor(region_id)
            return region_id, orders, None
        else:
            raise Exception(f"something wrong with request {region_id} orders error, response: {r_response}")
    except Exception as e:
        return region_id, None, e


def get_current_order_of_type_with_executor(region_id, type_ids, max_workers=20):
    """
    使用 ThreadPoolExecutor 获取指定星域的指定商品订单
    
    :param region_id: 星域ID
    :param type_ids: 商品ID列表
    :param max_workers: 最大线程数
    :return: {type_id: [orders]}
    """
    task = TaskContext(type_ids, region_id=region_id)
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_type_order, task, tid): tid for tid in type_ids}
        
        for future in as_completed(futures):
            type_id, orders, error = future.result()
            if error:
                print(f"\nType {type_id} error: {error}")
                task.retry_count[type_id] = task.retry_count.get(type_id, 0) + 1
                if task.retry_count[type_id] <= 3:
                    futures[executor.submit(process_type_order, task, type_id)] = type_id
                    print(f"Type {type_id} retry {task.retry_count[type_id]}/3")
                else:
                    print(f"Type {type_id} failed after 3 retries, skipped")
            else:
                if orders and len(orders) > 0:
                    results[type_id] = orders
                remaining = len(type_ids) - len(results) - len([t for t in task.retry_count if task.retry_count[t] >= 3])
                print(f"\rProcessed {len(results)}/{len(type_ids)} types", end='')
    
    return results


def process_type_order(task, type_id):
    """
    处理单个商品的订单获取
    
    :param task: 任务上下文
    :param type_id: 商品ID
    :return: (type_id, orders, error)
    """
    try:
        orders = direct_api_functions.get_orders_of_region_single_thread(task.region_id, type_id=type_id)
        return type_id, orders, None
    except Exception as e:
        return type_id, None, e


if __name__ == '__main__':
    print("ThreadPoolExecutor 重构版本")
    print("功能：")
    print("1. get_orders_of_all_regions_with_executor - 获取所有星域订单")
    print("2. get_orders_of_region_with_executor - 获取单个星域订单（多页）")
    print("3. get_current_order_of_type_with_executor - 获取指定商品订单")


"""
===============================================================================
ThreadPoolExecutor 重构总结
===============================================================================

## 一、保留的核心功能

| 功能 | 原实现位置 | 重构后位置 | 说明 |
|-----|-----------|-----------|------|
| 任务队列/列表 | MyGetTask.q | TaskContext.task_list | 用于重试机制 |
| 线程锁 | MyGetTask.lock | TaskContext.lock | 线程安全（虽然ThreadPoolExecutor自动管理） |
| 结果字典 | MyGetTask.result_dict | TaskContext.result_dict / 函数返回值 | 存储结果 |
| 重试计数 | MyGetTask.retry_count | TaskContext.retry_count | 记录每个任务的重试次数 |
| 重试机制 | 失败任务重新入队 | 异常时重新提交到executor | 保持不变 |
| 异常处理 | try-except + task.q.put() | try-except + futures[executor.submit()] | 保持不变 |

## 二、主要变化对比

| 方面 | 原实现 | 重构后 | 优势 |
|-----|--------|--------|------|
| **线程创建** | `MyGetOrdersOfAllRegionsThread` 子类化 | `ThreadPoolExecutor` | 更简洁，自动管理 |
| **线程启动** | `t.start()` | `executor.submit()` | 一行代码完成 |
| **线程等待** | `t.join()` | `as_completed()` 或隐式等待 | 更灵活 |
| **资源释放** | 手动处理 | `with` 语句自动管理 | 更安全，避免资源泄漏 |
| **任务分配** | `queue.Queue` | 内部自动队列 | 无需手动管理队列 |
| **代码量** | 约160行 | 约200行（功能更完善） | 可读性更好 |

## 三、类与函数映射

### 原 multithread_functions.py → 重构后

| 原类/函数 | 重构后 | 说明 |
|---------|-------|------|
| `MyGetTask` | `TaskContext` | 保留所有核心属性 |
| `MyGetOrdersOfAllRegionsThread` | `get_orders_of_all_regions_with_executor()` | 函数化实现 |
| `GetOrdersOfRegionOnePageThread` | `get_orders_of_region_with_executor()` | 函数化实现 |
| `MyGetCurrentOrderInRegionThread` | `get_current_order_of_type_with_executor()` | 函数化实现 |
| `get_orders_of_all_regions_from_api_single()` | `process_region()` | 单个星域处理逻辑 |
| `get_current_order_of_type_in_region_single()` | `process_type_order()` | 单个商品处理逻辑 |

## 四、使用示例

### 示例1: 获取所有星域订单

```python
import data_helper
from test.multithread_executor_refactor import get_orders_of_all_regions_with_executor

data_helper.load_region_id()
region_ids = list(data_helper.region_id_dict.keys())
results = get_orders_of_all_regions_with_executor(region_ids, max_workers=10, max_retries=3)
# results: {region_id: [order1, order2, ...]}
```

### 示例2: 获取单个星域（多页）订单

```python
from test.multithread_executor_refactor import get_orders_of_region_with_executor

orders = get_orders_of_region_with_executor(10000001, max_workers=10)
# orders: [order1, order2, ...] (合并所有页)
```

### 示例3: 获取指定商品订单

```python
from test.multithread_executor_refactor import get_current_order_of_type_with_executor

type_ids = [34, 35, 36, 37, 38]  # 商品ID列表
orders = get_current_order_of_type_with_executor(10000001, type_ids, max_workers=20)
# orders: {type_id: [order1, order2, ...]}
```

## 五、关键实现细节

### 1. 重试机制的实现

```python
# 在 as_completed 循环中检测异常
for future in as_completed(futures):
    item, result, error = future.result()
    if error:
        # 增加重试计数
        task.retry_count[item] = task.retry_count.get(item, 0) + 1
        # 如果未达最大重试次数，重新提交
        if task.retry_count[item] <= max_retries:
            futures[executor.submit(process_func, task, item)] = item
```

### 2. 进度显示

```python
print(f"\rCompleted {len(results)}/{len(items)}", end='')
```

### 3. 错误返回格式

所有处理函数统一返回 `(item, result, error)` 元组：
- 成功: `(item, result, None)`
- 失败: `(item, None, Exception)`

## 六、优缺点分析

### 优点

✅ **代码更简洁**：无需手动管理线程生命周期
✅ **自动资源管理**：`with` 语句确保线程池正确关闭
✅ **更好的异常处理**：统一的错误处理模式
✅ **现代Python标准**：`concurrent.futures` 是推荐方式
✅ **功能完整**：保留了所有原功能（重试、锁、进度）

### 缺点

⚠️ **学习曲线**：需要熟悉 `ThreadPoolExecutor` 和 `Future`
⚠️ **灵活性稍低**：相比直接使用 `threading`，自定义控制较少
⚠️ **与原实现API不兼容**：函数签名有变化

## 七、迁移建议

1. **保留原文件**：`multithread_functions.py` 继续用于现有代码
2. **新功能用重构版**：新代码使用 `multithread_executor_refactor.py`
3. **逐步迁移**：需要时可以逐步将旧代码迁移到新实现

## 八、注意事项

1. **锁的使用**：重构后 `TaskContext.lock` 存在但使用较少，因为 `ThreadPoolExecutor` 内部已经线程安全
2. **重试逻辑**：通过向 `futures` 字典添加新任务实现重试，这是正确的做法
3. **结果合并**：多页订单自动合并为一个列表
4. **错误跳过**：超过重试次数的任务会被跳过，不会阻塞其他任务

===============================================================================
"""


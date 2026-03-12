import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from concurrent.futures import ThreadPoolExecutor, as_completed

import data_helper
import direct_api_functions


def get_region_type_ids(region_id):
    """获取单个星域的活跃商品ID"""
    type_ids = direct_api_functions.get_type_ids_have_active_order_in_region(region_id)
    return region_id, set(type_ids)


def get_multi_region_type_intersection(region_ids, min_regions=2):
    """
    获取多星域商品交集

    :param region_ids: 星域ID列表
    :param min_regions: 最少出现在多少个星域中
    :return: {type_id: [region_id_1, region_id_2, ...]}
    """
    regions_active_types_dict = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_region_type_ids, rid): rid for rid in region_ids}
        for future in as_completed(futures):
            region_id, type_ids = future.result()
            regions_active_types_dict[region_id] = type_ids  # 每个星域的活跃商品ID集合，星域id是key，商品id集合是value

    # 统计每个商品出现在多少个星域
    type_region_map = {} # 转换region_types为type_region_map，商品id是key，星域id列表是value
    for region_id, type_ids in regions_active_types_dict.items():
        for tid in type_ids:
            if tid not in type_region_map:  #tid是商品id，如果tid不在type_region_map中，就在type_region_map添加这个商品id为key
                type_region_map[tid] = []
            type_region_map[tid].append(region_id)  # 把星域id加入到type_region_map[tid]作为value（商品tid是key，星域regoin_id列表是value）

    # 筛选满足条件的商品
    active_types_regions_dict = {
        tid: regions    # 创建一个新字典，将出现次数大于等于min_regions的商品id筛选出来
        for tid, regions in type_region_map.items()
        if len(regions) >= min_regions  # 字典推导式
    }

    return active_types_regions_dict, regions_active_types_dict

def test_func(active_types_regions_dict, regions_active_types_dict):
    for tid, regions in active_types_regions_dict.items():
        for region_id in regions:
            market_order_list = direct_api_functions.get_market_orders_in_region(region_id, tid)
    return market_order_list


if __name__ == "__main__":
    direct_api_functions.set_serenity_server()
    data_helper.set_serenity_server()
    data_helper.load_region_id()

    region_ids = list(data_helper.region_id_dict.keys())[:3]  # 测试3个星域
    print(f"测试星域数: {len(region_ids)}")

    intersection = get_multi_region_type_intersection(region_ids, min_regions=2)
    print(f"交集商品数: {len(intersection)}")

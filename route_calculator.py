#!/usr/bin/env python3

import math
import itertools
import json
import data_helper


def systems_distance(solar_system_id_a: int, solar_system_id_b: int):
    a = data_helper.mapSolarSystems_dict[solar_system_id_a]
    b = data_helper.mapSolarSystems_dict[solar_system_id_b]
    ax = float(a['x'])
    bx = float(b['x'])
    ay = float(a['y'])
    by = float(b['y'])
    az = float(a['z'])
    bz = float(b['z'])

    distance = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2)

    return distance


def average_jump_distance():
    """
    连接星系之间的平均距离

    :return: 1.1518138075831978e+16, G取值暂定为3e+16
    """
    one_way_jumps_set = set()
    distance_sum = 0
    for p in data_helper.mapSolarSystemJumps_list:
        px = (p[1], p[0])
        if p not in one_way_jumps_set and px not in one_way_jumps_set:
            one_way_jumps_set.add(p)
    for i in one_way_jumps_set:
        distance_sum += systems_distance(i[0], i[1])

    return distance_sum / len(one_way_jumps_set)


def new_jump_list_with_security(security: float):
    tmp_jump_list = list()
    for j in data_helper.mapSolarSystemJumps_list:
        j0 = data_helper.mapSolarSystems_dict[j[0]]
        j1 = data_helper.mapSolarSystems_dict[j[1]]
        if j0['security'] >= security and j1['security'] >= security:
            tmp_jump_list.append(j)

    return tmp_jump_list


def astar_route_calc(start_system_id: int, dest_system_id: int, min_security=0.0):
    """
    A* 算法计算星际最少跳跃次数路径 TODO: 路径未能最优，有待后续调试

    :param start_system_id: 出发星系
    :param dest_system_id: 终点星系
    :param min_security: 路径上星系的最小安全等级（软性要求）
    :return: 路径上的星系id列表
    """

    def new_box(g: float, h: float, system_id: int, parent_system_id: int):
        box = dict()
        box['G'] = g
        box['H'] = h
        box['F'] = g + h
        box['system_id'] = system_id
        box['parent_system_id'] = parent_system_id
        return box

    g_i = 3e+16
    open_dict = dict()
    closed_dict = dict()
    start_box = new_box(0, systems_distance(start_system_id, dest_system_id), start_system_id, 0)
    open_dict[start_system_id] = start_box

    while True:
        if len(open_dict) == 0:  # 路径不存在，已经没有可以打开的绿色盒子了
            return []
        current_box = sorted(open_dict.items(), key=lambda x: x[1]['F'])[0][1]  # 取F值最小的box，
        # sorted输出[(33, {'id': 33, 'F': 2, ...}), (2, {...})]
        current_id = current_box['system_id']
        open_dict.pop(current_id)
        closed_dict[current_id] = current_box

        # 路径已经找到
        if current_id == dest_system_id:
            path_list = list()
            cursor_id = current_id
            while cursor_id != 0:
                path_list.append(cursor_id)
                cursor_id = closed_dict[cursor_id]['parent_system_id']
            path_list.reverse()
            return path_list  # path_list本身是一个堆栈结构，终点最先入栈，起点最后入栈。输出时翻转

        # 找到邻接的盒子，即找到连接的星系
        neighbours_list = list()
        for p in data_helper.mapSolarSystemJumps_list:
            if p[0] == current_id:
                neighbours_list.append(p[1])

        for s in neighbours_list:
            if s in closed_dict.keys():  # 邻居是红色盒子，跳过（到星系路径已经计算）
                continue
            else:
                actual_security = float(data_helper.mapSolarSystems_dict[s]['security'])
                if min_security != 0 and actual_security < min_security:
                    s_new_g = current_box['G'] + g_i * 10
                else:
                    s_new_g = current_box['G'] + g_i
                s_new_h = systems_distance(s, dest_system_id)
                s_new_f = s_new_g + s_new_h
                if s in open_dict.keys() and s_new_f > open_dict[s]['F']:  # 新的F值更小，更新绿色盒子的F值
                    continue
                else:
                    open_dict[s] = new_box(s_new_g, s_new_h, s, current_id)  # 将周边的白色盒子转换为绿色盒子


def route_calc(start_system_id: int, dest_system_id: int, min_security=0.0):
    r = data_helper.search_route_cache(start_system_id, dest_system_id, min_security)
    if len(r) == 0:
        pl = astar_route_calc(start_system_id, dest_system_id, min_security)
        data_helper.write_route_cache(pl, min_security)
        return pl
    else:
        return r


def optimal_route(start_system_id: int, waypoint_list: list, min_security=0.0):
    """
    给定一个起点及包含作为航标的星系id列表，计算经过所有航标最少跳跃数的路径
    :param start_system_id: 起点星系id
    :param waypoint_list: 作为航标的星系id列表
    :param min_security: 路径上星系的最小安全等级（软性要求）
    :return: 最少跳跃数路径上的星系id列表
    """
    waypoint_lists = itertools.permutations(waypoint_list)
    min_distance = 9999
    optimized_route = list()
    for wp_list in waypoint_lists:
        tmp_route = route_calc(start_system_id, wp_list[0], min_security)
        for i in range(len(wp_list) - 1):
            tmp_route.extend(route_calc(wp_list[i], wp_list[i + 1], min_security)[1:])
        if len(tmp_route) < min_distance:
            min_distance = len(tmp_route)
            optimized_route = tmp_route

    return optimized_route


def show_route_info(path_list: list, way_points=[]):
    if len(path_list) == 0:
        print("No route info.")
        return

    print('[{} Jumps] [{} {:.1f}]'.format((len(path_list) - 1), data_helper.get_system_name(path_list[0]),
          float(data_helper.mapSolarSystems_dict[path_list[0]]['security'])))
    for p in path_list[1:]:
        r = data_helper.get_system_name(p)
        if p in way_points:
            r = "[{}]".format(r)
        print(" -> {} {:.1f}".format(r, float(data_helper.mapSolarSystems_dict[p]['security'])), end='')
    print()


def trade_route_calc(start_system_id: int, type_id: int, min_security=0.0):
    """
    返回最佳的贸易路线

    :param start_system_id: 起点星系id
    :param type_id: 利润订单对应的商品编号
    :param min_security: 路径上星系的最小安全等级（软性要求）
    :return: 成交所有卖单的最佳路线, 成交所有买单的最佳路线（最后一个卖单星系为起点）, 航标列表
    """
    if type_id not in data_helper.detailed_profitable_orders_dict.keys():
        return []

    order_dict = data_helper.detailed_profitable_orders_dict[type_id]
    sell_orders = order_dict['sell']
    buy_orders = order_dict['buy']
    sell_system_id_set = set()
    buy_system_id_set = set()
    for order in sell_orders:
        sell_system_id_set.add(order['system_id'])
    for order in buy_orders:
        buy_system_id_set.add(order['system_id'])

    if len(sell_system_id_set) > 13 or len(buy_system_id_set) > 13:
        print("[WARING] Too many way points({}/{})".format(len(sell_system_id_set), len(buy_system_id_set)))
        choise = input("Are you sure to continue?(Y/N)")
        choise = choise.lower()
        if choise == 'y' or choise == 'yes':
            pass
        else:
            print("Quit calculating route...")
            return [], [], [], []

    finish_sell_orders_route = optimal_route(start_system_id, list(sell_system_id_set), min_security)
    finish_buy_orders_route = optimal_route(finish_sell_orders_route[-1], list(buy_system_id_set), min_security)

    return finish_sell_orders_route, finish_buy_orders_route, list(sell_system_id_set), list(buy_system_id_set)


if __name__ == '__main__':
    data_helper.delay_functions()
    # ##################测试trade_route()#################
    # start_system_id = 30000142
    # dest_system_id = 30002537  # 埃玛马克
    # path_list = route_calc(start_system_id, dest_system_id, 0.5)
    # print(path_list)
    # show_route_info(path_list)
    # # [30000142, 30000144, 30000139, 30002802, 30002801, 30002800, 30002768, 30002765, 30002766, 30002763, 30002707,
    # # 30002709, 30002710, 30002711, 30002706, 30002676, 30002680, 30002681, 30002682, 30002048, 30002049, 30002053,
    # # 30002543, 30002544, 30002568, 30002529, 30002530, 30002507, 30002506, 30002537] [29 Jumps] [吉他 0.9] -> 皮尔米特 1.0
    # # -> 乌尔仑 1.0 -> 库索蒙莫 0.8 -> 苏洛肯 0.7 -> 哈托莫 0.6 -> 犹达玛 0.5 -> 希瓦拉 0.6 -> 利维能 0.7 -> 特恩勒恩 0.9 -> 尤尼尔 0.9 -> 奥贝鲁勒
    # # 0.8 -> 埃迪尔勒 0.8 -> 斯特提勒 0.9 -> 多苏维特 0.8 -> 帕查尼尔 0.6 -> 奥格奈斯 0.5 -> 底托勒 0.5 -> 克勒列 0.5 -> 贝伊 0.6 -> 乌汀达 0.5 ->
    # # 赫克 0.5 -> 尤斯塔 0.9 -> 帕多尔 1.0 -> 昂加 1.0 -> 吉格 0.8 -> 埃维斯贝尔 0.8 -> 阿布德班 0.7 -> 奥索古尔 0.5 -> 埃玛马克 0.4
    #
    # start_system_id = 30000142
    # dest_system_id = 30005020  # 瑟伊林
    # path_list = route_calc(start_system_id, dest_system_id, 0.5)
    # print(path_list)
    # show_route_info(path_list)
    # # [30000142, 30000144, 30000139, 30002791, 30002805, 30002803, 30002768, 30002765, 30002764, 30002761, 30005015,
    # # 30005016, 30005019, 30005020] [13 Jumps] [吉他 0.9] -> 皮尔米特 1.0 -> 乌尔仑 1.0 -> 希尔帕拉 0.9 -> 安提利 0.7 -> 郡尼加什 0.6 ->
    # # 犹达玛 0.5 -> 希瓦拉 0.6 -> 哈塔卡尼 0.9 -> 卡斯简恩 0.9 -> 希恩彻尔 0.9 -> 维萨兰 0.8 -> 阿波鲁列 0.8 -> 瑟伊林 0.4

    # start_system_id = 30000142
    # dest_system_id = 30004969  # 奥苏拉尔特
    # path_list = route_calc(start_system_id, dest_system_id, 0.5)
    # print(path_list)
    # show_route_info(path_list)
    # # [30000142, 30000144, 30000139, 30002791, 30002805, 30002803, 30002768, 30002765, 30002764, 30002761, 30005015,
    # # 30005198, 30004969] [12 Jumps] [吉他 0.9] -> 皮尔米特 1.0 -> 乌尔仑 1.0 -> 希尔帕拉 0.9 -> 安提利 0.7 -> 郡尼加什 0.6 -> 犹达玛 0.5 ->
    # # 希瓦拉 0.6 -> 哈塔卡尼 0.9 -> 卡斯简恩 0.9 -> 希恩彻尔 0.9 -> 帕克什 0.8 -> 奥苏拉尔特 0.9

    # start_system_id = 30004969  # 奥苏拉尔特
    # dest_system_id = 30005020  # 瑟伊林
    # path_list = route_calc(start_system_id, dest_system_id, 0.5)
    # print(path_list)
    # show_route_info(path_list)
    # # [30004969, 30004970, 30002633, 30002637, 30005020]
    # # [4 Jumps] [奥苏拉尔特 0.9]
    # #  -> 伦因 0.9 -> 杜安尼斯 0.6 -> 梅茨瑞 0.7 -> 瑟伊林 0.4

    # <<<<< 有问题 >>>>>
    # start_system_id = 30005020  # 瑟伊林
    # dest_system_id = 30002537  # 埃玛马克
    # path_list = astar_route_calc(start_system_id, dest_system_id, 0.5)
    # print(path_list)
    # show_route_info(path_list)
    # # [30005020, 30002637, 30002640, 30002636, 30002639, 30003034, 30002706, 30002676, 30002680, 30002681, 30002682,
    # # 30002048, 30002049, 30002053, 30002543, 30002544, 30002568, 30002529, 30002530, 30002507, 30002506, 30002537] [
    # # 21 Jumps] [瑟伊林 0.4] -> 梅茨瑞 0.7 -> 厄尔梅 0.8 -> 格里安卡尼 0.8 -> 埃卓蓝德 0.9 -> 玛提瑞 1.0 -> 多苏维特 0.8 -> 帕查尼尔 0.6 -> 奥格奈斯
    # # 0.5 -> 底托勒 0.5 -> 克勒列 0.5 -> 贝伊 0.6 -> 乌汀达 0.5 -> 赫克 0.5 -> 尤斯塔 0.9 -> 帕多尔 1.0 -> 昂加 1.0 -> 吉格 0.8 -> 埃维斯贝尔 0.8
    # # -> 阿布德班 0.7 -> 奥索古尔 0.5 -> 埃玛马克 0.4 [30005020, 30002637, 30002640, 30002636, 30002639, 30003034, 30002706,
    # # 30002676, 30002680, 30002681, 30002682, 30002048, 30002049, 30002053, 30002543, 30002544, 30002568, 30002529,
    # # 30002530, 30002507, 30002506, 30002537] [ 21 Jumps] [瑟伊林 0.4] -> 梅茨瑞 0.7 -> 厄尔梅 0.8 -> 格里安卡尼 0.8 -> 埃卓蓝德 0.9 ->
    # # 玛提瑞 1.0 -> 多苏维特 0.8 -> 帕查尼尔 0.6 -> 奥格奈斯 0.5 -> 底托勒 0.5 -> 克勒列 0.5 -> 贝伊 0.6 -> 乌汀达 0.5 -> 赫克 0.5 -> 尤斯塔 0.9 ->
    # # 帕多尔 1.0 -> 昂加 1.0 -> 吉格 0.8 -> 埃维斯贝尔 0.8 -> 阿布德班 0.7 -> 奥索古尔 0.5 -> 埃玛马克 0.4

    start_system_id = 30000144
    dest_system_id = 30003036  # 弗拉洛勒
    path_list = route_calc(start_system_id, dest_system_id, 0.5)
    print(path_list)
    show_route_info(path_list)
    # ##################测试读取路径缓存#################### start_system_id = 30002643 dest_system_id = 30002719 path_list =
    # data_helper.search_route_cache(start_system_id,dest_system_id) print( path_list) show_route_info(path_list)
    #
    # start_system_id = 30002719
    # dest_system_id = 30002643
    # path_list = data_helper.search_route_cache(start_system_id,dest_system_id)
    # print(path_list)
    # show_route_info(path_list)
    # print("len(path_list): {} [{}]".format(len(path_list), data_helper.get_system_name(path_list[0])))
    # for p in path_list[1:]:
    #     print(" -> {} {:.1f}".format(data_helper.get_system_name(p),
    #                              float(data_helper.mapSolarSystems_dict[p]['security'])), end='')
    # print()
    # ##################测试路径记录写入缓存####################
    # test_list = [30000144, 30002642, 30002643, 30002644, 30002691, 30002718, 30002719, 30002720, 30002050, 30002051, 30002060, 30002066, 30002099, 30002517, 30002537]
    # data_helper.write_route_cache(test_list)
    # test_list = [30000142, 30000144, 30002642, 30002643, 30002644, 30002691, 30002718, 30002719, 30002723, 30002053]
    # data_helper.write_route_cache(test_list)
    # ##################测试最优路径####################
    # # 目标 a - c - b 8跳
    # # 初始 a - b - c 11跳
    # a = 30000144  # 皮米
    # b = 30000137  # 尤斯库仑
    # c = 30010141  # 萨肯达
    # # 初始
    # path_list = astar_route_calc(a, b)
    # print('[{} Jumps]'.format(len(path_list) - 1))
    # for p in path_list[1:]:
    #     print(" -> {} {:.1f}".format(data_helper.get_system_name(p),
    #                              float(data_helper.mapSolarSystems_dict[p]['security'])), end='')
    # print()
    # path_list = astar_route_calc(b, c)
    # print('[{} Jumps]'.format(len(path_list) - 1))
    # for p in path_list[1:]:
    #     print(" -> {} {:.1f}".format(data_helper.get_system_name(p),
    #                              float(data_helper.mapSolarSystems_dict[p]['security'])), end='')
    # print()
    # # 优化
    # path_list = optimal_route(a, [b, c])
    # print('[{} Jumps]'.format(len(path_list) - 1))
    # for p in path_list[1:]:
    #     print(" -> {} {:.1f}".format(data_helper.get_system_name(p),
    #                              float(data_helper.mapSolarSystems_dict[p]['security'])), end='')
    # ###############################################
    #
    # path_list = astar_route_calc(30004009, 30004802)
    # path_list = astar_route_calc(30004402, 30004704)
    # path_list = astar_route_calc(30002537, 30000144)
    # path_list = astar_route_calc(30000144, 30002537)  # 皮米-埃玛马克
    # path_list = astar_route_calc(30000142, 30004486)  # 吉他 - 6-ELQP
    # path_list = astar_route_calc(30000142, 30002053)  # 吉他 - 赫克
    # print(path_list)
    # print("len(path_list): {} [{}]".format(len(path_list), data_helper.get_system_name(path_list[0])))
    # for p in path_list[1:]:
    #     print(" -> {} {:.1f}".format(data_helper.get_system_name(p),
    #                              float(data_helper.mapSolarSystems_dict[p]['security'])), end='')
    # path_list = astar_route_calc(30000144, 30002537, 0.5)  # 皮米-埃玛马克
    # # path_list = astar_route_calc(30000142, 30004486, 0.5)  # 吉他 - 6-ELQP
    # path_list = astar_route_calc(30000142, 30002053, 0.5)  # 吉他 - 赫克
    #
    # print(path_list)
    # print("len(path_list): {}".format(len(path_list)))
    # for p in reversed(path_list):
    #     print(data_helper.get_system_name(p))

    # for p in path_list:
    #     print("{} {:.1f}".format(data_helper.get_system_name(p), float(data_helper.mapSolarSystems_dict[p]['security'])))
    # print(average_jump_distance())
    # a = '30000142'  # jita
    # b = '30000144'  # 皮米
    # c = '30000145'  # 新加达里
    # m = '30004402'  # QYZM-W
    # n = '30004704'  # ZDYA-G
    # y = '30002788'  # 伊纳洛
    # z = '30003504'  # 米亚尔加
    # x = '30004802'  # M0O-JG
    # print("吉他 <->  皮米：{}".format(systems_distance(a,b)))  # 1.9891363019980264e+16
    # print("吉他 <->  新加：{}".format(systems_distance(a,c)))  # 1.1276924398525776e+16
    # print("49-U6U <-> 4-07MU: {}".format(systems_distance(30004009,30001260))) # 1.7201906610754048e+17
    # print("伊纳洛 <-> 米亚尔加：{}".format(systems_distance(y,z)))  # 1.2108909481534299e+17

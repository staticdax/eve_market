#!/usr/bin/env python3

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph
import pyqtgraph.opengl as gl
import numpy as np
import data_helper

color_Sienna2 = (238 / 255, 121 / 255, 66 / 255, 1)


def main():
    w = gl.GLViewWidget()
    w.opts['distance'] = 50
    w.show()
    w.setWindowTitle('EVE Starmap')

    # g = gl.GLGridItem()
    # w.addItem(g)
    # ###################### 调试 显示所有星域 ######################
    data_helper.delay_functions()
    system_dict = data_helper.mapSolarSystems_dict
    system_coordinate_dict = dict()
    dx, dy, dz, num = 0, 0, 0, 0
    # 星域 Forge
    for sid in range(10000001, 10000005):
    # for sid in data_helper.region_id_dict.keys():
        f = filter(lambda x: int(x['regionID']) == sid, system_dict.values())
        # f = filter(lambda x: x['regionID'] == '10000002', system_dict.values())
        # 所有星域
        # f = system_dict.values()

        for i in f:
            xyz = [i['x'], i['y'], i['z']]
            xyz = [i['x'] / 1e+15, i['y'] / 1e+15, i['z'] / 1e+15]
            system_coordinate_dict[i['solarSystemID']] = xyz
        pos = np.asarray(list(system_coordinate_dict.values()))

        n = len(system_coordinate_dict)
        num += n
        size = np.zeros(n)
        color = np.zeros((n, 4))
        for i in range(n):
            size[i] = 1
            color[i] = color_Sienna2
        # color[32] = (1,1,1,1)
        sp = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        w.addItem(sp)
        # 视角调整到所有坐标的中心位
        for o in system_coordinate_dict.values():
            dx += o[0]
            dy += o[1]
            dz += o[2]

    dx, dy, dz = dx / num, dy / num, dz / num
    w.pan(dx, dy, dz)

    # ###################### 显示星域 ######################
    # data_helper.delay_functions()
    # system_dict = data_helper.mapSolarSystems_dict
    # system_coordinate_dict = dict()
    # # 星域 Forge
    # # f = filter(lambda x: x['regionID'] == '10000002', system_dict.values())
    # # 所有星域
    # f = system_dict.values()
    #
    # for i in f:
    #     xyz = [i['x'], i['y'], i['z']]
    #     xyz = [i['x'] / 1e+15, i['y'] / 1e+15, i['z'] / 5e+15]
    #     system_coordinate_dict[i['solarSystemID']] = xyz
    # pos = np.asarray(list(system_coordinate_dict.values()))
    #
    # n = len(system_coordinate_dict)
    # size = np.zeros(n)
    # color = np.zeros((n, 4))
    # for i in range(n):
    #     size[i] = 1
    #     color[i] = color_Sienna2
    # color[32] = (1,1,1,1)
    # sp = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
    # w.addItem(sp)
    # # 视角调整到所有坐标的中心位
    # dx, dy, dz = 0, 0, 0
    # for o in system_coordinate_dict.values():
    #     dx += o[0]
    #     dy += o[1]
    #     dz += o[2]
    # dx, dy, dz = dx / n, dy / n, dz / n
    # w.pan(dx, dy, dz)
    #
    # # 显示路径 region forge
    # # region_id = 10000002
    # # f = filter(lambda x: data_helper.validate_system_is_in_region(x[0], region_id) and data_helper.validate_system_is_in_region(x[1], region_id),
    # #            [p for p in data_helper.mapSolarSystemJumps_list])
    # # for connected_system_id_pair in f:
    # #     pos = data_helper.get_ndarray_of_tow_systems_coordinates(connected_system_id_pair[0], connected_system_id_pair[1])
    # #     color = color_Sienna2
    # #     color = (1,0,0,1)
    # #     for p in pos:
    # #         p[0], p[1], p[2] = p[0]/1e+15, p[1]/1e+15, p[2]/5e+15
    # #     line = gl.GLLinePlotItem(pos=pos, color=color)
    # #     w.addItem(line)

    # ###################### 校准用 ######################
    # p = np.array((1, 1, 0))
    # size = 1
    # color = np.array((0, 0, 1, 2))
    # sp1 = gl.GLScatterPlotItem(pos=p, size=size, color=color, pxMode=False)
    # w.addItem(sp1)
    #
    # p0 = np.array((0, 0, 0))
    # size = 1
    # color0 = np.array((1, 0, 0, 2))
    # sp0 = gl.GLScatterPlotItem(pos=p0, size=size, color=color0, pxMode=False)
    # w.addItem(sp0)

    # pos = np.asarray(((0,0,0), (1,1,1)))
    # line = gl.GLLinePlotItem(pos=pos, color=color_Sienna2)
    # w.addItem(line)

    # ###################### 测试 100个散点 ######################
    # num = 30
    # ptest = np.zeros((num, 3))
    # size_test = np.zeros(num)
    # color_test = np.zeros((num, 4))
    # for i in range(len(ptest)):
    #     ptest[i] += i
    #     size_test[i] = 1
    #     color_test = (0, 1, 0, 2)
    # sptest = gl.GLScatterPlotItem(pos=ptest, size=size_test, color=color_test, pxMode=False)
    # w.addItem(sptest)

    # jita_data = data_helper.mapSolarSystems_dict[30000142]
    # jx = jita_data['x']
    # jy = jita_data['y']
    # jz = jita_data['z']
    # size = 20
    # color = np.array((1,0,1,2))
    # p = np.array((jx, jy, jz))
    # sp2 = gl.GLScatterPlotItem(pos=p, size=size, color=color, pxMode=False)
    # w.addItem(sp2)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    import sys

    main()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

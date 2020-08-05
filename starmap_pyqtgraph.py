#!/usr/bin/env python3

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph
import pyqtgraph.opengl as gl
import numpy as np
import data_helper


def main():
    app = QtGui.QApplication([])
    w = gl.GLViewWidget()
    w.opts['distance'] = 20
    w.show()
    w.setWindowTitle('EVE Starmap')

    g = gl.GLGridItem()
    w.addItem(g)

    data_helper.delay_functions()
    system_dict = data_helper.mapSolarSystems_dict
    system_list = list()
    f = filter(lambda x:x['regionID'] == '10000002', system_dict.values())
    for i in f:
        xyz = [i['x'], i['y'], i['z']]
        xyz = [i['x']/1e+15, i['y']/1e+15, i['z']/1e+15]
        system_list.append(xyz)

    pos = np.asarray(system_list)
    size = 5
    color = np.array((0, 0, 1, 1))

    sp = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
    w.addItem(sp)

    # p = np.array((0,0,0))
    # size = 10
    # color = np.array((0,0,1,2))
    # sp1 = gl.GLScatterPlotItem(pos=p, size=size, color=color, pxMode=False)
    # w.addItem(sp1)

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
    import sys
    main()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
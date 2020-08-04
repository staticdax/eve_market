#!/usr/bin/env python3

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import data_helper

data_helper.delay_functions()

jita_data = data_helper.mapSolarSystems_dict[30000142]
jx = jita_data['x']
jy = jita_data['y']
jz = jita_data['z']

z = np.linspace(0, 13, 1000)
x = 5 * np.sin(z)
y = 5 * np.cos(z)

fig = plt.figure()
ax1 = Axes3D(fig)

# ax1.scatter3D(jx, jy, jz, cmap='Blues')
# ax1.plot3D(x, y, z, 'gray')
f = filter(lambda x: x['regionID'] == '10000002', data_helper.mapSolarSystems_dict.values())
for system in f:
    x = system['x']/1e+16
    y = system['y']/1e+16
    z = system['z']/1e+16
    ax1.scatter3D(x, y, z, cmap='Blues')

plt.show()

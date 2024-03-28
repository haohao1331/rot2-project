import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
path = Path('/Volumes/Seagate Portable Drive/2024-03-20_10-45-01_SC20_closedloop_pilot/Record Node 102/experiment1/recording1/continuous/Neuropix-PXI-100.ProbeA-AP/continuous.dat')

data = np.memmap(path, dtype='int16', mode='r')
print(data.shape)

sr = 30000

data = data.reshape(-1, 384).T
print(data.shape)

ch0 = data[0, :data.shape[1]//30000*30000]
ch0 = ch0.reshape(-1, 30000)
print(ch0.shape)

ch0_std = np.std(ch0, axis=1)
np.save('ch0_std.npy', ch0_std)

plt.plot(ch0_std)
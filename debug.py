import numpy as np
import matplotlib.pyplot as plt
import pickle as pk
import pandas as pd
from pathlib import Path

def fill_in_null(data):
    # Find indices of null values
    null_indices = np.isnan(data)
    
    # Find indices of valid values
    valid_indices = np.where(~null_indices)[0]

    interp_data = np.nan * np.empty(data.shape)
    
    # Interpolate null values using linear interpolation
    interp_data[null_indices] = np.interp(np.where(null_indices)[0], valid_indices, data[valid_indices])
    
    edge_idx = np.diff(null_indices.astype(int))
    edge_idx1 = np.where(edge_idx > 0)[0]
    edge_idx2 = np.where(edge_idx < 0)[0]

    # print(data[edge_idx1])
    # print(data[edge_idx2+1])
    interp_data[edge_idx1] = data[edge_idx1]
    interp_data[edge_idx2+1] = data[edge_idx2+1]

    return interp_data
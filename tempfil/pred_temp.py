import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime
import os
from osgeo import gdal
import pandas as pd

def rec_lst(ts, atc):
    """
    Estimates pixel value of missing pixel using information from surrounding pixels.

    Args:
        ts (numpy.ndarray): Input 2D array representing pixel values.
        atc (numpy.ndarray): Input 2D array representing Annual Temperature Cycle.

    Returns:
        float: Estimated pixel value.
    """
    wx, wy = ts.shape[0], ts.shape[1]
    cp_x, cp_y = wx // 2, wy // 2
    
    if np.isnan(ts[cp_x, cp_y]):
        ls = np.abs(atc[cp_x, cp_y] - atc)
        sd_atc = np.std(atc)
        rs = 2 * sd_atc / 4
        r, c = np.where(ls <= rs)
        sp = np.stack((r, c), axis=1)
        msp = sp
        for m in range(len(msp) - 1, -1, -1):
            if np.isnan(ts[msp[m][0], msp[m][1]]):
                msp = np.delete(msp, m, axis=0)
        D1s = np.zeros(len(msp))
        D2s = np.zeros(len(msp))
        ws = np.zeros(len(msp))
        for t in range(len(msp)):
            D1s[t] = 1 + 2 * (np.sqrt((msp[t, 0] - wy)**2 + (msp[t, 1] - wx)**2)) / 4
            D2s[t] = np.abs(atc[msp[t, 0], msp[t, 1]] - atc[cp_x, cp_y])
            if D2s[t] == 0:
                continue
            ws[t] = D1s[t] * np.log(1 + D2s[t])
            ws[t] = 1 / ws[t]
        weight_sum = np.sum(ws)
        if weight_sum != 0:
            weight = ws / weight_sum
            rts = atc[cp_x, cp_y]
            for m in range(len(msp)):
                if not np.isnan(ts[msp[m][0], msp[m][1]]):
                    right = weight[m] * (ts[msp[m][0], msp[m][1]] - atc[msp[m][0], msp[m][1]])
                    rts += right
        else:
            rts = atc[cp_x, cp_y]
    else:
        rts = ts[cp_x, cp_y]
    return rts

def m_window(ts, atc, window_radius, stride=1):
    """
    Applies a moving window to estimate missing pixel values.

    Args:
        ts (numpy.ndarray): Input 2D array representing pixel values.
        atc (numpy.ndarray): Input 2D array representing Annual Temperature Cycle.
        window_radius (int, optional): Size of the moving window. Defaults to 10.
        stride (int, optional): Stride of the moving window. Defaults to 1.

    Returns:
        numpy.ndarray: Array with estimated pixel values.
    """
    padimage_1 = np.pad(ts, window_radius, 'reflect')
    padimage_2 = np.pad(atc, window_radius, 'reflect')
    output = np.zeros_like(ts)

    for i in range(ts.shape[0]):
        for j in range(ts.shape[1]):
            indx_i = i + window_radius
            indx_j = j + window_radius
            if indx_i + window_radius + 1 <= padimage_1.shape[0] and indx_j + window_radius + 1 <= padimage_1.shape[1]:
                output[i, j] = rec_lst(padimage_1[indx_i - window_radius:indx_i + window_radius + 1, indx_j - window_radius:indx_j + window_radius + 1],
                                   padimage_2[indx_i - window_radius:indx_i + window_radius + 1, indx_j - window_radius:indx_j + window_radius + 1])

    return output

def create_georeferenced_tif(reference_tif, array_2d, output_path):
    """
    Creates a georeferenced TIFF file from a 2D array.

    Args:
        reference_tif (str): Path to a reference TIFF file.
        array_2d (numpy.ndarray): 2D array representing pixel values.
        output_path (str): Output path for the new TIFF file.

    Returns:
        gdal.Dataset: Output georeferenced TIFF file.
    """
    ds = gdal.Open(reference_tif)
    gt = ds.GetGeoTransform()
    res = gt[1]
    xmin = gt[0]
    ymax = gt[3]
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    xstart = xmin + res/2
    ystart = ymax - res/2
    x = np.arange(xstart, xstart+xsize*res, res)
    y = np.arange(ystart, ystart-ysize*res, -res)
    x = np.tile(x, ysize)
    y = np.repeat(y, xsize)
    flatee = array_2d.flatten()
    dfn1 = pd.DataFrame({"x": x, "y": y, "value": flatee})
    dfn1.to_csv(r"data\array_2d.xyz", index=False, header=None, sep=" ")
    output_tif = gdal.Translate(output_path, r"data\array_2d.xyz", outputSRS="EPSG:32649")
    ds = None
    return output_tif
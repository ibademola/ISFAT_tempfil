import os
import numpy as np
from osgeo import gdal
from datetime import datetime, timedelta
from scipy.optimize import curve_fit

def extract_pixel_value(file_path, x, y):
    dataset = gdal.Open(file_path)
    bandd = dataset.GetRasterBand(1).ReadAsArray()
    pixel_value = bandd[x, y]
    return pixel_value

def get_acquisition_time(file_name):
    acquisition_time = file_name.split('.')[0]  # Extracting the time part from the filename
    return acquisition_time

# Function to convert UTC to HKT
def utc_to_hkt(utc_datetime_str):
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y%m%d_%H%M')
    hkt_datetime = utc_datetime + timedelta(hours=8)
    return hkt_datetime.strftime('%Y%m%d_%H%M')

# Function for daytime temperature cycle model
def daytime_temperature_cycle(x, T0, Ta, A, tm, tsr):
    omega = (4/3) * (tm - tsr)
    return T0 + Ta * np.cos(np.pi / omega * (x - tm))

# Function for nighttime temperature cycle model
def nighttime_temperature_cycle(x, T0, Ta, A, tm, tsr, delta_T, B, C):
    omega = (4/3) * (tm - tsr)
    k = omega / np.pi * (1 / np.tan(np.pi / omega * (tsr - tm)) - (delta_T / Ta) * (1 / np.sin(np.pi / omega * (tsr - tm))))
    return T0 + delta_T + ((Ta * np.cos(np.pi / omega * (tsr - tm))) - delta_T) * k / (k + x - tsr) + B * (x - tsr) + C * ((x - tsr) ** 2)

def get_dtc_best_fit_parameters_and_lst(time, pixel_values_dict):
    acquisition_times_hr = []
    pixel_valuesT = []                                           

    for datetime_str, value in pixel_values_dict.items():
        # Extract the last four characters of the datetime string to get the time (HHMM)
        time_str = datetime_str[-4:]
        hour = int(time_str[:2])
        if hour < 6:
            hour += 24  # Adjust hours for plotting
        acquisition_times_hr.append(hour)  # Extract hours for plotting on x-axis
        if value >= 260 and value != -3.402823e+38:  # Filter values less than 260 and omit invalid pixel values
            pixel_valuesT.append(value)
        else:
            pixel_valuesT.append(np.nan)

    # Filter out NaN values
    valid_indices = np.where(~np.isnan(pixel_valuesT))[0]
    if len(valid_indices) == 0:
        return np.nan  # Return NaN if there are no valid pixel values

    acquisition_times_hr_valid = np.array(acquisition_times_hr)[valid_indices]
    pixel_valuesT_valid = np.array(pixel_valuesT)[valid_indices]

    # Separate daytime and nighttime indices
    daytime_indices = [i for i, hr in enumerate(acquisition_times_hr_valid) if 6 <= hr < 19]
    nighttime_indices = [i for i, hr in enumerate(acquisition_times_hr_valid) if hr >= 19]
    x = datetime.strptime(time, '%Y-%m-%d_%H%M').hour

    if 6 <= x < 19:
        popt, pcov_daytime = curve_fit(daytime_temperature_cycle, acquisition_times_hr_valid[daytime_indices], pixel_valuesT_valid[daytime_indices], bounds=([-np.inf, -np.inf, -np.inf, 6, 5], [np.inf, np.inf, np.inf, 18, 260])) 
        lst_value = daytime_temperature_cycle(x, *popt)
    else:
        popt, pcov_nighttime = curve_fit(nighttime_temperature_cycle, acquisition_times_hr_valid[nighttime_indices], pixel_valuesT_valid[nighttime_indices], bounds=([-np.inf, -np.inf, -np.inf, 19, 5, 0, -np.inf, -np.inf], [np.inf, np.inf, np.inf, 23, 260, 20, np.inf, np.inf]))
        lst_value = nighttime_temperature_cycle(x, *popt)
     
    return lst_value

def get_dtc_array(folder_path, time):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tif'):  # Assuming all Landsat files are TIFFs
            file_path = os.path.join(folder_path, file_name)
            dataset = gdal.Open(file_path)
            rows = dataset.RasterYSize
            cols = dataset.RasterXSize
            break  # We assume all TIFF files have the same dimensions

    dtc_array = np.zeros((rows, cols), dtype=float)
   
    for x in range(cols):
        for y in range(rows):
            # Initialize dictionary to store pixel (x,y) values on different acquisition days
            pixel_values_dictT = {}

            for file_name in os.listdir(folder_path):
                if file_name.endswith('.tif'):  # Assuming all Landsat files are TIFFs
                    file_path = os.path.join(folder_path, file_name)
                    acquisition_time = get_acquisition_time(file_name)
                    pixel_value = extract_pixel_value(file_path, x, y)
                    pixel_values_dictT[str(acquisition_time)] = pixel_value

            pixel_values_dictT = {utc_to_hkt(datetime_str): value for datetime_str, value in pixel_values_dictT.items()}
            dtc_array[x, y] = get_dtc_best_fit_parameters_and_lst(time, pixel_values_dictT)

    return dtc_array
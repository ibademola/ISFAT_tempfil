import time
import logging
from tempfil import (
    get_dtc_array, 
    m_window, 
    np_from_tif, 
    format_time,
    create_georeferenced_tif,
)


# Start time for measuring processing time
start_time = time.time()

# Example usage:
folder_path = r"C:\ISFAT_tempfil\data\crop_H8_22"
timee = '2022-01-06_1000'  # Example time of the day (in HKT, format: YYYY-MM-DD_HHMM)
testing = get_dtc_array(folder_path, timee)
window_radius = 10

input_file_path = r"C:\ISFAT_tempfil\data\crop_H8_22\Clip_20221224_1000.tif"
data = np_from_tif(input_file_path)
ooo = r"D:\Obj2\test22.tif"
reconstruct = m_window(data, testing, window_radius)
output_tif = create_georeferenced_tif(input_file_path, reconstruct, ooo)

import numpy as np
def mean_squared_error(true_values, predicted_values):
    return np.mean((true_values - predicted_values) ** 2)

def mean_absolute_error(true_values, predicted_values):
    return np.mean(np.abs(true_values - predicted_values))

def r2_score(true_values, predicted_values):
    true_mean = np.mean(true_values)
    ss_total = np.sum((true_values - true_mean) ** 2)
    ss_residual = np.sum((true_values - predicted_values) ** 2)
    r2 = 1 - (ss_residual / ss_total)
    return r2

def calculate_metrics(true_values, predicted_values):
    # Reshape arrays to 1D
    true_values = true_values.flatten()
    predicted_values = predicted_values.flatten()
    
    # Calculate RMSE
    rmse = np.sqrt(mean_squared_error(true_values, predicted_values))
    
    # Calculate R-square
    rsquare = r2_score(true_values, predicted_values)
    
    # Calculate MAE
    mae = mean_absolute_error(true_values, predicted_values)
    
    return rmse, rsquare, mae

ppp = r"C:\ISFAT_tempfil\data\crop_22_1000\Clip_20221224_1000.tif"
true_values = np_from_tif(ppp)
predicted_values = reconstruct

rmse, rsquare, mae = calculate_metrics(true_values, predicted_values)
print("MAE:", mae)
print("RMSE:", rmse)
print("R-square:", rsquare)

# Calculate processing time
processing_time_seconds = time.time() - start_time
processing_time_formatted = format_time(processing_time_seconds)

print("missing LST pixels reconstructed successfully.", f"Processing time: {processing_time_formatted}")

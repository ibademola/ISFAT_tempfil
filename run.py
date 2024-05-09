import time
import logging
from tempfil import (
    get_atc_array, 
    m_window, 
    np_from_tif, 
    format_time,
    create_georeferenced_tif,
)


# Start time for measuring processing time
start_time = time.time()

folder_path = 'data\crop_L8_36'
input_file_path = r"data\crop_L8_36\LC08_L1TP_122044_20220106_20220114_02_T1.tif.tif"
date = '2022-01-06'
window_radius = 10
output_path = r"D:\Obj2\test7.tif"

a = get_atc_array(
    input_file_path, 
    folder_path, date, 
    window_radius
)

Ts_f = np_from_tif(input_file_path)

pred_arr = m_window(Ts_f, a, windowsize=10)

output_tif = create_georeferenced_tif(
    input_file_path, 
    pred_arr, 
    output_path
)


# Calculate processing time
processing_time_seconds = time.time() - start_time
processing_time_formatted = format_time(processing_time_seconds)


# Log processing time
logging.info(f"Processing time: {processing_time_formatted}")

print("missing LST pixels reconstructed successfully.", f"Processing time: {processing_time_formatted}")




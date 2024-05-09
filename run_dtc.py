import time
import logging
from tempfil import (
    get_dtc_array, 
    m_window, 
    np_from_tif, 
    format_time,
    create_georeferenced_tif,
)

# Example usage:
folder_path = r"D:\Obj2\h8105\hh105"
timee = '2022-01-06_1000'  # Example time of the day (in HKT, format: YYYY-MM-DD_HHMM)
testing = get_dtc_array(folder_path, timee)

reconstruct = m_window(data, testing, windowsize=10)


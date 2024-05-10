import time
import logging
from tempfil import (
    get_atc_array, 
    get_dtc_array,
    m_window, 
    np_from_tif, 
    format_time,
    create_georeferenced_tif,
)

def main(folder_path, input_file_path, date, window_radius, output_path, tempfill_type, time_of_day):
    """
    Main function to reconstruct missing LST pixels.

    Args:
        folder_path (str): Path to the folder containing Landsat files.
        input_file_path (str): Path to the input raster file.
        date (str): Date for which to generate LST (required for 'annual').
        window_radius (int): Radius of the surrounding window for missing pixels.
        output_path (str): Output path for the new TIFF file.
        tempfill_type (str): Type of tempfill ('annual' or 'diurnal').
        time_of_day (str): Time of the day for diurnal tempfill (required for 'diurnal').
    """
    # Start time for measuring processing time
    start_time = time.time()

    if tempfill_type == 'annual':
        a = get_atc_array(input_file_path, folder_path, date, window_radius)
    elif tempfill_type == 'diurnal':
        a = get_dtc_array(folder_path, time_of_day)
    else:
        raise ValueError("Invalid tempfill_type. Supported values are 'annual' or 'diurnal'.")

    Ts_f = np_from_tif(input_file_path)
    pred_arr = m_window(Ts_f, a, window_radius)
    create_georeferenced_tif(input_file_path, pred_arr, output_path)

    # Calculate processing time
    processing_time_seconds = time.time() - start_time
    processing_time_formatted = format_time(processing_time_seconds)

    # Log processing time
    logging.info(f"Processing time: {processing_time_formatted}")

    print("missing LST pixels reconstructed successfully.", f"Processing time: {processing_time_formatted}")

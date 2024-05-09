import time
import logging
from tempfil import (
    get_atc_array, 
    m_window, 
    np_from_tif, 
    format_time,
    create_georeferenced_tif,
)

def main(folder_path, input_file_path, date, window_radius, output_path):
    """
    Main function to reconstruct missing LST pixels.

    Args:
        folder_path (str): Path to the folder containing Landsat files.
        input_file_path (str): Path to the input raster file.
        date (str): Date for which to generate LST.
        window_radius (int): Radius of the surrounding window for missing pixels.
        output_path (str): Output path for the new TIFF file.
    """
    # Start time for measuring processing time
    start_time = time.time()

    a = get_atc_array(input_file_path, folder_path, date, window_radius)
    Ts_f = np_from_tif(input_file_path)
    pred_arr = m_window(Ts_f, a, window_radius)
    create_georeferenced_tif(input_file_path, pred_arr, output_path)

    # Calculate processing time
    processing_time_seconds = time.time() - start_time
    processing_time_formatted = format_time(processing_time_seconds)

    # Log processing time
    logging.info(f"Processing time: {processing_time_formatted}")

    print("missing LST pixels reconstructed successfully.", f"Processing time: {processing_time_formatted}")

if __name__ == "__main__":
    # User input for parameters
    folder_path = input("Enter path to folder containing annual LST images: ") 
    input_file_path = input("Enter path to LST with missing pixels: ")
    date = input("Enter acqusition date of LST imageto be reconstructed 'YYYY-MM-DD:' ")
    window_radius = int(input("Enter window radius: "))
    output_path = input("Enter path to save reconstructed LST image: ") 

    main(folder_path, input_file_path, date, window_radius, output_path)

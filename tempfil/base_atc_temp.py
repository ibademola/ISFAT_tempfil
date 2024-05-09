import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime
import os
from osgeo import gdal

def extract_pixel_value(file_path, x, y):
    """
    Extracts pixel value at given coordinates from a raster file.

    Args:
        file_path (str): Path to the raster file.
        x (int): Row index.
        y (int): Column index.

    Returns:
        float: Pixel value at the specified coordinates.
    """
    dataset = gdal.Open(file_path)
    band_data = dataset.GetRasterBand(1).ReadAsArray()
    pixel_value = band_data[x, y]
    return pixel_value


def get_acquisition_date(file_name):
    """
    Extracts acquisition date from Landsat file name.

    Args:
        file_name (str): Landsat file name.

    Returns:
        datetime.date: Acquisition date extracted from the file name.
    """
    date_str = file_name.split('_')[3]  # Extracting the date part from the filename
    acquisition_date = datetime.strptime(date_str, '%Y%m%d').date()
    return acquisition_date

def annual_temperature_cycle(x, A, B, C, D):
    """
    Defines the annual temperature cycle model.

    Args:
        x (float): Day of year.
        A (float): Amplitude.
        B (float): Phase shift.
        C (float): Linear component.
        D (float): Constant component.

    Returns:
        float: Modeled temperature.
    """
    return A * np.sin(2 * np.pi * x / 365.25 + B) + C * x + D

def get_best_fit_parameters_and_lst(date, pixel_values_dict):
    """
    Fits the annual temperature cycle model to observed pixel values.

    Args:
        date (str): Date for which to predict temperature.
        pixel_values_dict (dict): Dictionary containing pixel values for different acquisition dates.

    Returns:
        float: Predicted temperature for the specified date.
    """
    acquisition_dates = []
    acquisition_dates_doy = []
    pixel_values = []

    for date_str, value in pixel_values_dict.items():
        if 265 <= value <= 320:  # Filtering valid pixel values
            acquisition_dates.append(date_str)
            acquisition_dates_doy.append(datetime.strptime(date_str, '%Y-%m-%d').timetuple().tm_yday)
            pixel_values.append(value)

    # Fitting the temperature cycle model to observed data
    popt, _ = curve_fit(annual_temperature_cycle, acquisition_dates_doy, pixel_values)

    # Calculating temperature for the specified date
    x = datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday
    lst_value = annual_temperature_cycle(x, *popt)

    return lst_value

def find_missing_pixels(input_file_path, window_radius):
    """
    Identifies missing pixels in a raster file and returns surrounding window.

    Args:
        input_file_path (str): Path to the input raster file.
        window_radius (int): Radius of the surrounding window.

    Returns:
        list: List of coordinates representing the surrounding window of missing pixels.
    """
    input_dataset = gdal.Open(input_file_path)
    input_array = input_dataset.GetRasterBand(1).ReadAsArray()
    missing_pixels = set()
    surrounding_window = set()

    rows, cols = input_array.shape

    # Iterating through the input array to identify missing pixels
    for i in range(rows):
        for j in range(cols):
            if input_array[i, j] < 12 or input_array[i, j] > 400:  # Checking pixel value range
                missing_pixels.add((i, j))
                for x in range(max(0, i - window_radius), min(rows, i + window_radius + 1)):
                    for y in range(max(0, j - window_radius), min(cols, j + window_radius + 1)):
                        surrounding_window.add((x, y))

    # Converting set to list with 2D array representation
    surrounding_window = [[index[0], index[1]] for index in surrounding_window]

    return surrounding_window

def get_atc_array(input_file_path, folder_path, date, window_radius):
    """
    Generates an array of Land Surface Temperature (LST) using the Annual Temperature Cycle (ATC) model.

    Args:
        input_file_path (str): Path to the input raster file.
        folder_path (str): Path to the folder containing Landsat files.
        date (str): Date for which to generate LST.
        window_radius (int): Radius of the surrounding window for missing pixels.

    Returns:
        numpy.ndarray: Array of ATC base LST values.
    """
    # Getting dimensions from the first available Landsat file
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tif'):
            file_path = os.path.join(folder_path, file_name)
            dataset = gdal.Open(file_path)
            rows = dataset.RasterYSize
            cols = dataset.RasterXSize
            break

    atc_array = np.zeros((rows, cols), dtype=float)  # Array for storing LST values

    # Finding missing pixels and their surrounding window
    missing_pixels = find_missing_pixels(input_file_path, window_radius)

    # Generating LST values for missing pixels
    for index in missing_pixels:
        x, y = index
        pixel_values_dict = {}

        # Extracting pixel values for different acquisition dates
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.tif'):
                file_path = os.path.join(folder_path, file_name)
                acquisition_date = get_acquisition_date(file_name)
                pixel_value = extract_pixel_value(file_path, x, y)
                pixel_values_dict[str(acquisition_date)] = pixel_value

        # Getting LST value using the ATC model
        atc_array[x, y] = get_best_fit_parameters_and_lst(date, pixel_values_dict)

    return atc_array

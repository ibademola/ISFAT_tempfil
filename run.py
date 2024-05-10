import logging
import input_handler
import main_function

if __name__ == "__main__":
    # Get tempfill type
    tempfill_type = input_handler.get_tempfill_type()

    # Get parameters based on tempfill type
    if tempfill_type == 'annual':
        folder_path, input_file_path, date, window_radius, output_path, _ = input_handler.get_annual_parameters()
        time_of_day = None  # No need for time_of_day when tempfill_type is annual
    elif tempfill_type == 'diurnal':
        folder_path, input_file_path, _, window_radius, output_path, time_of_day = input_handler.get_diurnal_parameters()
        date = None  # No need for date when tempfill_type is diurnal
    else:
        print("Invalid tempfill_type. Supported values are 'annual' or 'diurnal'.")
        exit()

    # Call main function
    main_function.main(folder_path, input_file_path, date, window_radius, output_path, tempfill_type, time_of_day)

def get_tempfill_type():
    tempfill_type = input("Enter tempfill type ('annual' or 'diurnal'): ")
    return tempfill_type

def get_annual_parameters():
    folder_path = input("Enter path to folder containing annual LST images: ") 
    input_file_path = input("Enter path to LST with missing pixels: ")
    date = input("Enter acquisition date of LST image to be reconstructed (format: YYYY-MM-DD): ")
    window_radius = int(input("Enter window radius: "))
    output_path = input("Enter path to save reconstructed LST image: ")
    return folder_path, input_file_path, date, window_radius, output_path, None

def get_diurnal_parameters():
    folder_path = input("Enter path to folder containing diurnal LST images: ") 
    input_file_path = input("Enter path to LST with missing pixels: ")
    window_radius = int(input("Enter window radius: "))
    output_path = input("Enter path to save reconstructed LST image: ")
    time_of_day = input("Enter time of the day (format: YYYY-MM-DD_HHMM): ")
    return folder_path, input_file_path, None, window_radius, output_path, time_of_day

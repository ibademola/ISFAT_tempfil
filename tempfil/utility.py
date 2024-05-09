import time
from osgeo import gdal
import numpy as np

# Function to convert seconds to hours:minutes:seconds format
def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def np_from_tif(tiffile):
    df = gdal.Open(tiffile)
    df_np = df.GetRasterBand(1).ReadAsArray()
    df_np[(df_np < 200) | (df_np > 400)] = np.nan
    return df_np



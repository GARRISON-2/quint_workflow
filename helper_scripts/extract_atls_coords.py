import json
import numpy as np
import cv2
from pathlib import Path
import requests

# grab binary .flat file
flat_f = Path('S:/anshutz/Cruz-Martin_Lab/projects/TBI_Project/quint_workflow/local_data/stain_run_1/PNGs/20251013_FT_24hrs_Sag9_ID57476/s001_composite_dwnscl_nl.flat')


def grab_coords(height, width):

    with open(flat_f, "rb") as ff:
        fl_array = np.fromfile(ff, dtype=np.uint8)


    # Reshape into a 3D grid: (Height, Width, 3 RGB channels)
    # This will throw an error if the file size doesn't match width * height * 3
    atlas_map = fl_array.reshape((height, width, 3))

    # Your FICTURE DataFrame
    ficture_df = pd.DataFrame({
        'x_coord': [150, 450],
        'y_coord': [200, 300]
    })

    def get_rgb_color(row):
        x = int(row['x_coord'])
        y = int(row['y_coord'])
        
        if 0 <= y < height and 0 <= x < width:
            # Returns a tuple of (R, G, B)
            return tuple(atlas_map[y, x])
        return (0, 0, 0) # Background

    ficture_df['rgb_color'] = ficture_df.apply(get_rgb_color, axis=1)





#import PyNutil 
from pathlib import Path
import subprocess
import gc
import tifffile
from PIL import Image

# grab current working directory
PROJ_ROOT = Path.cwd()

dir24 = "/Xenium/TBI 24hrs"
dir48 = "/Xenium/TBI 48hrs"
dir48_MH2 = "/Xenium/TBI 48hrs + MH2"

png_output_dir =  PROJ_ROOT / "local_data" / "dapi_run_1" / "pngs"

mask_dir = PROJ_ROOT 
atlas_dir = PROJ_ROOT
out_dir = PROJ_ROOT

# # Grabbing input folders/files
# folder_list = []

# # set which image file type to search for in the directory
# file_type = "*.tif"

# for folder in folder_list:

#     # grab all files of file_type in chosen input directory
#     path_list = in_dir.rglob(file_type)

class IMG_PACK():
    def __init__(self, image_path):
        self.in_path = image_path
        self.png_path = None

    def makePNGCopy(self, output_dir, png_width = 1500, png_height=1000):
        # create png path name
        png_path = Path(str(output_dir) + self.in_path.stem + '_dwnscl')

        print(self.in_path)

        # open input image using Pillow
        with Image.open(self.in_path) as img:

            # resize image to desired ratio
            ds_img = img.resize((png_width, png_height))

            # convert to rgb and then save png copy of the input image. the original image remains unchanged
            ds_img.convert("RGB").save(png_path)
            self.png_path = png_path
        

    def getPNGSize(self):
          # open input image using Pillow
        try:
            with Image.open(self.png_path) as png:

                return png.size

        except Exception as e:
            return (f"ERROR - Unable to open image. {e}")
        


check_img = True

IP_list = []

# loop through all input image files from glob list
for path in path_list:
#     # make image pack to cleanly hold paths for current file
    IP = IMG_PACK(path)

#     # create downscaled png copy
    IP.makePNGCopy(output_dir=png_output_dir)

    if check_img:
        with Image.open(IP.png_path) as png:
            print(f"New png path: {IP.png_path}. png size: {IP.getPNGSize()}")

    IP_list.append(IP)




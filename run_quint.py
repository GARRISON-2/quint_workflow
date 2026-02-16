from pathlib import Path
import subprocess
from PIL import Image
import gc

PROJ_ROOT = Path(__file__).parent

in_dir = PROJ_ROOT / 'local_data/test_folder/empty_tiffs'
mask_dir = PROJ_ROOT
atlas_dir = PROJ_ROOT
out_dir = PROJ_ROOT


class IMG_PACK():
    def __init__(self, image_path):
        in_path = image_path
        png_path = None

    def makePNGCopy(self, png_width = 1500, png_height=1000):
        # create png path name
        png_path = self.in_path.with_name(self.in_path.stem + "_ds.png")

        # open input image using Pillow
        img = Image.open(self.in_path)

        # resize image to desired ratio
        ds_img = img.resize((png_width, png_height))

        # convert to rgb and then save png copy of the input image. the original image remains unchanged
        ds_img.convert("RGB").save(png_path)
        self.png_path = png_path


# set which image file type to seach for in the directory
file_type = "*.tif"

# grab all files of file_type in chosen input directory
path_list = list(in_dir.rglob(file_type))


# loop through all input image files from glob list
for path in path_list:
    # make image pack to cleanly hold paths for current file
    IP = IMG_PACK(path)

    # create downscaled png copy
    IP.makePNGCopy()
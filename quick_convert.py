from pathlib import Path
import tifffile
import xml.etree.ElementTree as ET
from skimage import transform, exposure, color, io
import sys
import numpy as np
import time


class IMG_PACK():
    def __init__(self, image_path):
        self.tif_path = image_path
        self.png_path = None
        self.png_array = None

    def makePNGCopy(self, output_dir, LUT, png_shape = (1500, 1000)):
        # create png path name
        png_path = Path(output_dir / (self.tif_path.stem + '_dwnscl.png'))

        # ensure all channels are together in the same directory before reading. 
        # element[0] = should be equal to the number of channels
        with tifffile.TiffFile(f) as tif:
            # grab xml info from first file
            if i == 0:
                ome_xml = tif.ome_metadata
                root = ET.fromstring(ome_xml)

                # Format xml then output
                ET.indent(root)
                print(ET.tostring(root, encoding="unicode"))

            # save as array
            print("Loading tif array...")
            img_arr = tif.pages[0].asarray()

        print(f"Array shape: {img_arr.shape}")  # e.g. (C, Y, X) for multi-channel stains
        print(f"Array data type: {img_arr.dtype}")
        print(f"Array size: {img_arr.nbytes} bytes")

        print(f"Downscaling channel...")

        # Downscale the image array
        ds_array = transform.resize(img_arr, png_shape, preserve_range=True, anti_aliasing=False)

        print(f"Channel Downscaling complete")

        # delete the original array to free up memory
        del img_arr

        print(f"Applying color...")
        ds_array = ds_array[:, :, np.newaxis] * LUT

        print(f"Saving PNG...")

        ds_array = self.autoscale(ds_array)

        # normalize to uint8 before saving
        io.imsave(png_path, exposure.rescale_intensity(ds_array, out_range=(0, 255)).astype(np.uint8))

        # save variables to object
        self.png_path = png_path
        self.png_array = ds_array


    def autoscale(self, channel, low=1, high=99, gamma=0.5):
        p_low = np.percentile(channel, low)
        p_high = np.percentile(channel, high)
        clipped = np.clip(channel, p_low, p_high)

        # normalize to 0-1 for gamma, then scale back to uint16
        normalized = (clipped - p_low) / (p_high - p_low)
        gamma_corrected = np.power(normalized, gamma) * 65535

        return gamma_corrected

# path of directory containing tif files
input_dir = Path("S:\\Anshutz\\Cruz-Martin_Lab\\projects\\TBI_Project\\data")

# grab all tif files with releavant naming format, then sort 
files = sorted(input_dir.glob("ch*.ome.tif"))

output_dir = Path("S:/Anshutz/Cruz-Martin_Lab/projects/TBI_Project/quint_workflow/local_data/stain_run_1/pngs/")





# lookup table colors 
lut_colors = [
    [1,0,1],    #ch0000 - (DAPI)
    [0,1,0],    #ch0001 - (ATP1A1)
    [0,0,1],    #ch0002 - (18s)
    [1,1,0]     #ch0003 - (alphasma)
]

pks = []
png_shape = (
    1000,   # height
    1500    # width
    )

mem_save = True # if less than 32gbs of ram, this is recommended.

for i, (f, col) in enumerate(zip(files, lut_colors)):
    chnl_strt = time.time()
    
    pks.append(IMG_PACK(f))

    pks[i].makePNGCopy(output_dir, lut_colors[i])

    if i == 0:
        comp_array = np.zeros((pks[i].png_array.shape[0], 
                               pks[i].png_array.shape[1], 
                               3), 
                               dtype=np.float64)
        
    comp_array += pks[i].png_array

np.clip(comp_array, 0, 65535)
comp_array = exposure.rescale_intensity(comp_array, out_range=(0, 255)).astype(np.uint8)

io.imsave(Path(output_dir / 'composite_dwnscl.png'), comp_array)



print("All channels downscaled.")
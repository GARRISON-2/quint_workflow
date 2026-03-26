from pathlib import Path
import tifffile
import xml.etree.ElementTree as ET
#from skimage import transform, exposure, color, io
import sys
import numpy as np
import time
import cv2


class IMG_PACK():
    def __init__(self, image_path):
        self.tif_path = image_path
        self.png_path = None
        self.png_array = None

    def makePNGCopy(self, output_dir, LUT, max_ht = 1500, max_wd=1000, save_img = True):
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
        
        # calculte scale for array resizing
        scale = min(max_ht / img_arr.shape[0], max_wd / img_arr.shape[1])

        png_shape = (
            int(img_arr.shape[0] * scale),
            int(img_arr.shape[0] * scale)
        )

        # Downscale the image array
        ds_array = cv2.resize(img_arr, png_shape, interpolation=cv2.INTER_AREA)

        print(f"Channel Downscaling complete")

        # delete the original array to free up memory
        del img_arr

        print(f"Applying color...")
        ds_array = ds_array[:, :, np.newaxis] * LUT #cv2 uses BGR instead of RGB
        ds_array = ds_array[:, :, ::-1]

        print(f"Saving PNG...")

        ds_array = self.autoscale(ds_array)

        if save_img:
            # normalize to uint8 before writing 
            png_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(png_path), cv2.normalize(ds_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))
        
        # save variables to object
        self.png_path = png_path
        self.png_array = ds_array


    def autoscale(self, channel, low=1, high=99, gamma=0.85):
        p_low = np.percentile(channel, low)
        p_high = np.percentile(channel, high)
        clipped = np.clip(channel, p_low, p_high)

        # normalize to 0-1 for gamma, then scale back to uint16
        normalized = (clipped - p_low) / (p_high - p_low)
        gamma_corrected = np.power(normalized, gamma) * 65535

        return gamma_corrected

# path of directory containing tif files
input_dir = Path("S:\\Anshutz\\Cruz-Martin_Lab\\projects\\TBI_Project\\data")
output_dir = Path("S:/Anshutz/Cruz-Martin_Lab/projects/TBI_Project/quint_workflow/local_data/stain_run_1/pngs/")

# lookup table colors 
# lut_colors = [
#     [1,0,0],    #ch0000 - (DAPI)
#     [0,1,0],    #ch0001 - (ATP1A1)
#     [0,0,1],    #ch0002 - (18s)
#     [1,0,1]     #ch0003 - (alphasma)
# ]

# QuPath equivalent Settings:
lut_colors = [
    [1,0,0],    #ch0000 - (DAPI)
    [0,1,0],    #ch0001 - (ATP1A1)
    [0,0,1],    #ch0002 - (18s)
    [1,1,0]     #ch0003 - (alphasma)
]

pks = []
png_shape = (
    1500,   # height
    1000    # width
    )

# grab all tif files with releavant naming format, then sort 
files = sorted(input_dir.rglob("ch*.ome.tif"))

for i, f in enumerate(files):
    # create specific ouput directoy variable to handle output subdirectories
    out_spec = output_dir

    chnl_strt = time.time()
    
    pks.append(IMG_PACK(f))

    # ensure output file directory structure matches input
    for fp in f.parents:
        if fp.name != input_dir.name:
            out_spec = out_spec / fp.name
        else:
            break

    pks[i].makePNGCopy(out_spec, lut_colors[i % len(lut_colors)])

    # set & reset compisite array using input image shape
    if i == 0 or (i > 0 and i % len(lut_colors) == 0):
        comp_array = np.zeros((pks[i].png_array.shape[0], 
                               pks[i].png_array.shape[1], 
                               3), 
                               dtype=np.float64)
   
    comp_array += pks[i].png_array

    # output compisite image after a channel batch is complete
    if (i + 1) % len(lut_colors) == 0:
        # remove values not between 0 - 65535
        comp_array = np.clip(comp_array, 0, 65535)

        # normalize array from uint16(as float64) to uint8 range and data type
        comp_array = cv2.normalize(comp_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


        # ---Compatibililty adjustments for QUICKNII---

        # grab height and width of array to calculate center
        height, width = comp_array.shape[:2]
        center = (width // 2, height // 2)
        M = cv2.getRotationMatrix2D(center, angle=-45, scale=1.0)

        # calculate new dimensions to avoid clipping the corners
        cos = np.abs(M[0, 0]) # grab cos value from rotation matrix
        sin = np.abs(M[0, 1]) # grab sin value from rotation matrix
        new_w = int(height * sin + width * cos) # new width is combination original height horizontal (via sin) contributations & original widths horizontally (via cos) contributions
        new_h = int(height * cos + width * sin)

        # adjust rotation matrix to account for shift
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        comp_array = cv2.warpAffine(comp_array, M, (new_w, new_h))

        # pad outside with empty black-space 
        comp_array = cv2.copyMakeBorder(
            comp_array,
            top=0,
            bottom=0,
            left=50,
            right=50,
            borderType=cv2.BORDER_CONSTANT,
            value=[0,0,0]
        )
 
        # remove some blank space from top & bottom
        comp_array = comp_array[100:-100, :, :]

        # output the current composite img
        cv2.imwrite(Path(out_spec / f's001_composite_dwnscl.png'), comp_array)   
 
print("All channels downscaled.")

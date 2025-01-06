from PIL import Image
import os
import random
import numpy as np
import tifffile as tiff 
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--input_file")
parser.add_argument("--output_dir")
parser.add_argument("--n_copies", type=int, default=2)

args = parser.parse_args()
input_file = args.input_file
output_dir = args.output_dir
n_copies = args.n_copies 

pad_limit = 4

for c in range(n_copies):

    pad = random.randint(1, pad_limit) 
    filename = os.path.split(input_file)[-1]
    output_file  = os.path.join(output_dir, filename.replace(".tif", f"_{c}.tif"))
    print(pad)
    imarray = tiff.imread(input_file) 
    im_shape = imarray.shape 
    im_shape_ext = tuple([i+2*pad for i in list(im_shape[:-1])]) + (im_shape[-1],)
    print(im_shape_ext)
    output = np.zeros(im_shape_ext)
    print(output.shape)
    output[pad:-pad, pad:-pad, :] = imarray
    print(output.shape)
    tiff.imwrite(output_file, output)

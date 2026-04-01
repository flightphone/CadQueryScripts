import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter

def any_nonzero_pooling(input_path, output_path, block_size=8):
    """
    Свёртка: если в блоке block_size×block_size хоть один пиксел > 0,
    весь блок становится белым (255), иначе чёрным (0).
    """
    img = Image.open(input_path).convert('L')  # grayscale
    arr = np.array(img, dtype=np.uint8)
    result = (maximum_filter(arr, size=block_size) > 0).astype(np.uint8) * 255
    Image.fromarray(result).save(output_path)

any_nonzero_pooling("./stl/lens.png", "./stl/lens_mask.png", block_size=32)    
    
import os
import numpy as np
from rembg import remove, new_session
from PIL import Image

def clean_white_edges(img, border_size=3, white_threshold=240):
    """Clean up remaining white pixels near transparent edges."""
    data = np.array(img)
    # Find pixels that are near-white and semi/fully opaque
    is_white = (
        (data[:, :, 0] > white_threshold) &
        (data[:, :, 1] > white_threshold) &
        (data[:, :, 2] > white_threshold) &
        (data[:, :, 3] > 0)
    )
    # Find transparent pixels
    is_transparent = data[:, :, 3] == 0

    # Dilate transparent region to find border zone
    from scipy.ndimage import binary_dilation
    border_zone = binary_dilation(is_transparent, iterations=border_size) & ~is_transparent

    # Make white pixels in the border zone transparent
    cleanup_mask = is_white & border_zone
    data[cleanup_mask, 3] = 0

    return Image.fromarray(data)

def process_fishing_gear(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    session = new_session("isnet-general-use")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing: {filename}...")

            input_path = os.path.join(input_dir, filename)
            img = Image.open(input_path)

            # 1. Remove background with rembg (no alpha matting)
            no_bg = remove(img, session=session)

            # 2. Clean up white fringe near edges
            no_bg = clean_white_edges(no_bg, border_size=3, white_threshold=240)

            # 3. Auto-crop transparent space
            bbox = no_bg.getbbox()
            if bbox:
                cropped = no_bg.crop(bbox)
            else:
                cropped = no_bg

            # 4. Save as PNG
            output_name = os.path.splitext(filename)[0] + ".png"
            cropped.save(os.path.join(output_dir, output_name))

    print("Done! Check your output folder.")

process_fishing_gear('raw_images', 'processed_images')

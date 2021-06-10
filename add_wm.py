#!/usr/local/bin/python3
"""
add_wm.py image_dir
Usage:
    add_wm.py [options]

Options:
    -h --help           Show this text.
    -d --dir <directory images> directory to watermark
"""

import numpy as np
import glob
import cv2
import os
from docopt import docopt


def increase_brightness(image, value=18):
    """Increases the brightness of an image.

    Args:
      image: image object to edit.
      value: amount of brightness to add, default is 18.

    Returns:
      image object.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return image


def add_transparent_watermark(base_image, overlay_image):
    """Takes in two images with transparency and applies the 'overlay_image' as a watermark.
    Both images must be the same resolution.

    Args:
      base_image: image used as the base image.
      overlay_image: image used as the watermark.

    Returns:
      image object.
    """
    # Split out the transparency mask from the color info
    watermark_img = overlay_image[:, :, :3]
    watermark_mask = overlay_image[:, :, 3:]

    # Calculate the inverse mask
    background_mask = 255 - watermark_mask

    # Turn background_mask into three channel, so we can use weight
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

    # Create a masked out base image, and masked out watermark
    # Convert the images to floating point in range 0.0 - 1.0
    base_part = (base_image * (1 / 255.0)) * (background_mask * (1 / 255.0))
    watermark_part = (watermark_img * (1 / 255.0)) * (background_mask * (1 / 255.0))

    # Add them together, rescale back to an 8bit integer image
    return np.uint8(cv2.addWeighted(base_part, 255.0, watermark_part, 255.0, 0.0))

def main():
    opts = docopt(__doc__)
    image_dir = opts['--dir']

    types = ('*.png', '*.jpg', '*.jpeg')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(f"./{image_dir}/{files}"))

    count = 0
    for i in files_grabbed:
        print(f'Loading: {i}')
        # Load image to edit
        img = cv2.imread(i, -1)

        # Load watermark image
        watermark_image = cv2.imread("./watermark/DP-Watermark.png", -1)

        # Increase brightness on image
        brighter_image = increase_brightness(image=img, value=18)

        # Specify image dimensions
        width = 756
        height = 756
        dimensions = (width, height)

        # Resize image
        original_resized_image = cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)
        resized_image = cv2.resize(brighter_image, dimensions, interpolation=cv2.INTER_AREA)

        # Resize watermark image
        resized_watermark_image = cv2.resize(watermark_image, dimensions, interpolation=cv2.INTER_AREA)

        # Add overlay to image
        image_with_watermark = add_transparent_watermark(base_image=resized_image,
                                                         overlay_image=resized_watermark_image)
        curr_path = f"./{image_dir}/"
        image_name = i.rsplit('\\', 1)[-1]
        print(f'... Adding wm: {count}-{image_name}\n')

        cv2.imwrite(os.path.join(curr_path, f"{count}-{image_name}"), image_with_watermark)
        count = count + 1


if __name__ == '__main__':
    main()

from PIL import Image
from io import BytesIO
import folder_paths as comfy_paths
import hashlib
import numpy as np
import os
import requests
import torch

TEXT_TYPE = "STRING"

class BrevLoadImage:
    def __init__(self):
        self.input_dir = comfy_paths.input_directory

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {"default": './ComfyUI/input/example.png', "multiline": False}),
                "RGBA": (["false", "true"],),
            },
            "optional": {
                "filename_text_extension": (["true", "false"],),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", TEXT_TYPE)
    RETURN_NAMES = ("image", "mask", "filename_text")
    FUNCTION = "load_image"

    CATEGORY = "BrevMage"

    def load_image(self, image_path, RGBA='false', filename_text_extension="true"):
        RGBA = (RGBA == 'true')

        try:
            i = Image.open(image_path)
        except OSError:
            if image_path.startswith('http'):
                # Extract the filename from the URL
                filename = os.path.basename(image_path)
                # Construct the downloaded file path
                downloaded_path = f"{self.input_dir}/{filename}"
                try:
                    i = Image.open(downloaded_path)
                except OSError:
                    print(f"The downloaded image `{downloaded_path}` cannot be opened!")
                    i = Image.new(mode='RGB', size=(512, 512), color=(0, 0, 0))
            else:
                print(f"The image `{image_path.strip()}` specified doesn't exist!")
                i = Image.new(mode='RGB', size=(512, 512), color=(0, 0, 0))

        if not i:
            return

        # Rest of the code remains the same

        return (image, mask, filename)

    def download_image(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return img
        except requests.exceptions.RequestException as err:
            print(f"Error downloading image: {err}")

    @classmethod
    def IS_CHANGED(cls, image_path):
        if image_path.startswith('http'):
            return float("NaN")
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

NODE_CLASS_MAPPINGS = {
    "BrevImage": BrevLoadImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BrevImage": "BrevImage Node"
}

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
                    "RGBA": (["false","true"],),
                },
                "optional": {
                    "filename_text_extension": (["true", "false"],),
                    "use_opt_directory": (["true", "false"],),
                }
            }

    RETURN_TYPES = ("IMAGE", "MASK", TEXT_TYPE)
    RETURN_NAMES = ("image", "mask", "filename_text")
    FUNCTION = "load_image"
    CATEGORY = "BrevMage"

    def load_image(self, image_path, RGBA='false', filename_text_extension="true", use_opt_directory="true"):
        print(f"Received image_path: {image_path}")
        print("The input dir is: ", self.input_dir)
        
        if use_opt_directory == "true":
            hardcoded_input_dir = "/opt/ComfyUI/input/"
        else:
            hardcoded_input_dir = "/runpod-volume/ComfyUI/input/"
        print("Hardcoded dir to use", hardcoded_input_dir)
        RGBA = (RGBA == 'true')

        if image_path.startswith('http'):
            from io import BytesIO
            i = self.download_image(image_path)
        else:
            try:
                new_image_path = hardcoded_input_dir + image_path
                print(f"Attempting to open image: {new_image_path}")
                i = Image.open(new_image_path)
                print(f"Successfully opened image: {new_image_path}")
            except OSError:
                print(f"The image `{new_image_path.strip()}` specified doesn't exist!")
                i = Image.new(mode='RGB', size=(512, 512), color=(0, 0, 0))
        if not i:
            return

        # Update history
        # update_history_images(image_path)

        image = i
        if not RGBA:
            image = image.convert('RGB')
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

        if filename_text_extension == "true":
            filename = os.path.basename(image_path)
            print(filename)
        else:
            filename = os.path.splitext(os.path.basename(image_path))[0]
            print(filename)
        print("Returning Image")
        return (image, mask, filename)

    def download_image(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return img
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: ({url}): {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Connection Error: ({url}): {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: ({url}): {errt}")
        except requests.exceptions.RequestException as err:
            print(f"Request Exception: ({url}): {err}")

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

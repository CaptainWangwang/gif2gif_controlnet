import modules.scripts as scripts
import gradio as gr
import os

from modules import images
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state
from PIL import Image
import numpy as np


class Script(scripts.Script):

    # The title of the script. This is what will be displayed in the dropdown menu.
    def title(self):

        return "gif2gif_controlnet"

    # Determines when the script should be shown in the dropdown menu via the
    # returned value. As an example:
    # is_img2img is True if the current tab is img2img, and False if it is txt2img.
    # Thus, return is_img2img to only show the script on the img2img tab.

    def show(self, is_img2img):

        return False

    # How the script's is displayed in the UI. See https://gradio.app/docs/#components
    # for the different UI components you can use and how to create them.
    # Most UI components can return a value, such as a boolean for a checkbox.
    # The returned values are passed to the run method as parameters.

    def ui(self, is_img2img):
        input_path = gr.Textbox(label="input gif full path")
        output_path = gr.Textbox(label="output gif full path")
        return [input_path, output_path]

    # This is where the additional processing is implemented. The parameters include
    # self, the model object "p" (a StableDiffusionProcessing class, see
    # processing.py), and the parameters returned by the ui method.
    # Custom functions can be defined here, and additional libraries can be imported
    # to be used in processing. The return value should be a Processed object, which is
    # what is returned by the process_images method.

    def run(self, p, input_path, output_path):
        print("type(p)")
        print(type(p))
        print("p")
        print(p)
        print("vars(p)")
        print(vars(p))

        gif_path = input_path

        def read_gif(path):
            im = Image.open(path)
            frames = []
            try:
                while True:
                    frames.append(im.copy())
                    im.seek(len(frames))  # 跳转到下一帧
            except EOFError:
                pass
            return im, frames

        gif, frames = read_gif(gif_path)

        procs = []
        for img in frames:
            img = img.convert("RGB")  # 把图片转换成RGB模式
            arr = np.asarray(img)  # 使用asarray()函数

            mask_channel = np.ones(arr.shape[:2], dtype=np.uint8)
            mask_channel[:, :] = 255
            mask = np.dstack((np.zeros(arr.shape, dtype=np.uint8), mask_channel))

            for e in p.script_args:
                if isinstance(e, dict) and 'image' in e and 'mask' in e:
                    e['image'] = arr
                    e['mask'] = mask
            print("vars(p_hacked)")
            print(vars(p))

            # p.do_not_save_samples = True

            proc = process_images(p)
            print("type(proc)")
            print(type(proc))
            print("proc")
            print(proc)
            print("vars(proc)")
            print(vars(proc))

            procs.append(proc)

        processed_imgs = [p.images[0] for p in procs]
        processed_imgs[0].save(output_path,
                               save_all=True,
                               append_images=processed_imgs[1:],
                               duration=gif.info['duration'],
                               loop=0)

        return procs[-1]
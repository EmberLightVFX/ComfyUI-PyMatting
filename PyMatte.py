import torch
import numpy as np
from pymatting import (
    estimate_alpha_cf,
    estimate_alpha_knn,
    estimate_alpha_lbdm,
    estimate_alpha_lkm,
    estimate_alpha_rw,
    estimate_alpha_sm,
    estimate_foreground_cf,
    estimate_foreground_ml,
    blend,
    stack_images,
    fix_trimap,
)


class PyMatte:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.modelname = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("IMAGE",),
                "alpha_alg": (
                    [
                        "cf",
                        "knn",
                        "lbdm",
                        "lkm",
                        "rw",
                        "sm",
                    ],
                    {"default": "lkm"},
                ),
                "forground_alg": (
                    [
                        "cf",
                        "ml",
                    ],
                    {"default": "cf"},
                ),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "IMAGE",
        "IMAGE",
        "IMAGE",
        "IMAGE",
    )
    RETURN_NAMES = (
        "alpha",
        "foreground",
        "new_image",
        "cutout",
        "color_bleeding",
    )
    FUNCTION = "elfx_alpha_matting"
    OUTPUT_NODE = False
    CATEGORY = "EmberLightVFX"

    def elfx_alpha_matting(
        self,
        image: torch.Tensor,
        mask: torch.Tensor,
        alpha_alg: str,
        forground_alg: str,
    ):
        ret_alpha: list[torch.Tensor] = []
        ret_foreground: list[torch.Tensor] = []
        ret_new_image: list[torch.Tensor] = []
        ret_cutout: list[torch.Tensor] = []
        ret_color_bleeding: list[torch.Tensor] = []
        for index, im in enumerate(image):
            # Load images
            img = im.cpu().numpy().astype(np.float64)
            trimap = (
                mask[index].cpu().numpy().astype(np.float64)[:, :, 0]
            )  # Use the red channel
            trimap = fix_trimap(trimap, 0.1, 0.9)

            # estimate alpha from image and trimap
            match alpha_alg:
                case "cf":
                    alpha = estimate_alpha_cf(img, trimap)
                case "knn":
                    alpha = estimate_alpha_knn(img, trimap)
                case "lbdm":
                    alpha = estimate_alpha_lbdm(img, trimap)
                case "lkm":
                    alpha = estimate_alpha_lkm(img, trimap)
                case "rw":
                    alpha = estimate_alpha_rw(img, trimap)
                case "sm":
                    alpha = estimate_alpha_sm(img, trimap)
                case _:
                    print(f"Coulnd't match {alpha_alg}, using IKM")
                    alpha = estimate_alpha_cf(img, trimap)

            # make gray background
            background = np.zeros(img.shape)
            background[:, :] = [0.5, 0.5, 0.5]

            # estimate foreground from image and alpha
            match forground_alg:
                case "cf":
                    foreground = estimate_foreground_cf(img, alpha)
                case "ml":
                    foreground = estimate_foreground_ml(img, alpha)
                case _:
                    print(f"Coulnd't match {forground_alg}, using CF")
                    foreground = estimate_foreground_cf(img, alpha)

            # blend foreground with background and alpha, less color bleeding
            new_image = blend(foreground, background, alpha)

            # save results in a grid
            # images = [image, trimap, alpha, new_image]
            # grid = make_grid(images)
            # save_image("lemur_grid.png", grid)

            # save cutout
            cutout = stack_images(foreground, alpha)
            # save_image("lemur_cutout.png", cutout)

            # just blending the image with alpha results in color bleeding
            color_bleeding = blend(img, background, alpha)
            # grid = make_grid([color_bleeding, new_image])
            # save_image("lemur_color_bleeding.png", grid)

            # Append result to return array

            ret_alpha.append(torch.from_numpy(alpha))
            ret_foreground.append(torch.from_numpy(foreground))
            ret_new_image.append(torch.from_numpy(new_image))
            ret_cutout.append(torch.from_numpy(cutout))
            ret_color_bleeding.append(torch.from_numpy(color_bleeding))
        return (
            ret_alpha,
            ret_foreground,
            ret_new_image,
            ret_cutout,
            ret_color_bleeding,
        )

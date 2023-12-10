from groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2

from diffusers import StableDiffusionInpaintPipeline
import torch
import numpy as np
from torchvision.ops import box_convert
from PIL import Image

def generate_masks_with_grounding(image_source, boxes):
    h, w, _ = image_source.shape
    boxes_unnorm = boxes * torch.Tensor([w, h, w, h])
    boxes_xyxy = box_convert(boxes=boxes_unnorm, in_fmt="cxcywh", out_fmt="xyxy").numpy()
    mask = np.zeros_like(image_source)
    for box in boxes_xyxy:
        x0, y0, x1, y1 = box
        mask[int(y0):int(y1), int(x0):int(x1), :] = 255
    return mask
def process_photo(IMAGE_PATH = "kam.jpg", 
                  TEXT_PROMPT = "face", 
                  BOX_TRESHOLD = 0.35, 
                  TEXT_TRESHOLD = 0.25,
                  prompt = "tatarka face"):
    
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-inpainting"
    )


    pipe = pipe.to("cpu")

    model = load_model("GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py", "GroundingDINO/weights/groundingdino_swint_ogc.pth", device = 'cpu')

    image_source, image = load_image(IMAGE_PATH)

    boxes, logits, phrases = predict(
        model=model,
        image=image,
        caption=TEXT_PROMPT,
        box_threshold=BOX_TRESHOLD,
        text_threshold=TEXT_TRESHOLD,
        device = 'cpu'
    )
    annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
    #cv2.imwrite('test1.jpg', annotated_frame)
    annotated_frame = annotated_frame[...,::-1]
    image_mask = generate_masks_with_grounding(image_source, boxes[0].unsqueeze(0))

    image_source = Image.fromarray(image_source)
    annotated_frame = Image.fromarray(annotated_frame)
    image_mask = Image.fromarray(image_mask)

    image_source_for_inpaint = image_source.resize((512, 512))
    image_mask_for_inpaint = image_mask.resize((512, 512))

    
    image_inpainting = pipe(prompt=prompt, image=image_source_for_inpaint, mask_image=image_mask_for_inpaint).images[0]
    image_inpainting = image_inpainting.resize((image_source.size[0], image_source.size[1]))

    cv2.imwrite(IMAGE_PATH[:-4] + '_pred.jpg', np.asarray(image_inpainting)[...,::-1])
    return np.asarray(image_inpainting)[...,::-1]

import random
import glob
import os

from PIL import Image


def placeholder(filepath):
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    path = os.path.join(os.path.dirname(__file__), "placeholders", "*.jpg")
    jpg = glob.glob(path)
    img = Image.open(random.choice(jpg))
    w, h = img.size
    crop = min(w, h)
    img2 = img.crop(((w - crop)//2,
                     (h - crop)//2,
                     (w + crop)//2,
                     (h + crop)//2)).resize((192, 192))
    img2.save(filepath)

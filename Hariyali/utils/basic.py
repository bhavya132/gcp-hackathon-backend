from Hariyali import schemas
from Hariyali.Database import models
from io import BytesIO
from PIL import Image
import base64
import uuid
import os
from Hariyali.utils.cloud_storage import CloudStorage

cloud_storage = CloudStorage()


def upload_user_image(user: schemas.UserCreate) -> str:
    tmp_name = ''.join(user.name.split()).lower()[:8]
    loc = f'{tmp_name}_{str(uuid.uuid4())}.jpg'
    file_loc = save_image_local(loc, user.display_picture)
    public_url = cloud_storage.upload(file_loc, loc)
    os.remove(file_loc)
    return public_url

def save_image_local(loc: str, img_b64: str):
    image_data = bytes(img_b64, encoding="ascii")
    im = Image.open(BytesIO(base64.b64decode(image_data)))
    im = im.convert("RGB")
    file_loc = os.path.join(os.getcwd(), loc)
    im.save(file_loc)
    return file_loc



def del_user_image(user: models.User):
    prefix = 'https://storage.googleapis.com/garden-storage/'
    img_url = user.display_picture
    img_name = img_url[len(prefix):]
    # cloud_storage.delete(img_name)

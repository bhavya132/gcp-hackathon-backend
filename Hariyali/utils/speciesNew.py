import base64
import requests
import os 
import json
from Hariyali.Database import models
API_KEY = "Ip3bjupV6E2ykIVPNsZFvITpidGheBkzrQlikHO7xjHjUgQBqN" #os.getenv("PLANT_ID_KEY")


def identify_plant(enc_img):
    images = [enc_img]
    # images.append(enc_img)
    # see the docs for more optional attributes
    # https://github.com/Plant-id/Plant-id-API/wiki/Plant-details
    params = {
        "api_key": API_KEY,
        "images": images,
        "modifiers": ["crops_fast"],
        "plant_language": "en",
        "plant_details": [
            "common_names",
            "edible_parts",
            "name_authority",
            "propagation_methods",
            "taxonomy",
            "url",
            "wiki_description",
            "wiki_image"
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.plant.id/v2/identify",
        json=params,
        headers=headers
    )
    print(response)
    # print("##############################")
    return response.json()


def get_species_from_src(img_src: str):
    with open(img_src, "rb") as imgFile:
        img_enc = base64.b64encode(imgFile.read()).decode("ascii")
    return identify_plant(img_enc)


def get_species(img_raw: bytes):
    img_enc = base64.b64encode(img_raw).decode("ascii")
    return identify_plant(img_enc)


def get_score(species_name: str, user: models.User):
    # Make a points based system later.
    found = False
    for i in user.plants:
        print(i.species)
        if i.species == species_name:
            found = True
            break
    if found:
        return 10
    return 50


# if __name__ == '__main__':
#     val = get_species_from_src("./pic1.jpeg")
#     print(json.dumps(val))

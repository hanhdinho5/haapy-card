import os
import re
import requests
import json
import random

API_KEY = "rOKw05DEUqvpYWdsKEADRkGS0La37whfj6D1MPiOoRq4vWkTrRj4Auak"
BASE_DIR = "/home/hanh-dinh/Downloads/Project/haapy-card/mau-thiep"

THEMES = {
    "thiep-sinh-nhat-nguoi-yeu": "birthday cake celebration",
    "thiep-sinh-nhat-hien-dai": "birthday cake celebration",
    "thiep-giang-sinh-an-lanh": "christmas tree",
    "thiep-chuc-suc-khoe": "get well soon flowers",
    "thiep-chuc-mung-tot-nghiep": "graduation cap",
    "thiep-to-tinh-lang-man": "romantic couple",
    "thiep-tinh-yeu-am-nhac": "romantic couple",
    "thiep-chuc-mung-nam-moi": "new year fireworks",
    "thiep-cam-on-thanh-lich": "thank you flowers",
    "thiep-cuoi-sang-trong": "wedding couple",
    "thiep-quoc-te-phu-nu": "beautiful woman flowers"
}

def get_pexels_images(query, count):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        photos = data.get("photos", [])
        random.shuffle(photos)
        links = [p["src"]["large"] for p in photos[:count]]
        # Pad if not enough
        while len(links) < count:
            links.append("https://images.pexels.com/photos/191429/pexels-photo-191429.jpeg?auto=compress&cs=tinysrgb&h=650&w=940")
        return links
    else:
        print(f"Failed to fetch for {query}: {response.text}")
        return [""] * count

templates = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

for t in templates:
    theme_key = t
    query = THEMES.get(theme_key, "beautiful")
    
    idx_path = os.path.join(BASE_DIR, t, "index.html")
    if not os.path.exists(idx_path):
        continue
        
    with open(idx_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find PAGE_IMAGES block
    match = re.search(r'const PAGE_IMAGES\s*=\s*(\{.*?\});', content, re.DOTALL)
    if match:
        images_block = match.group(1)
        # Count how many images are there
        img_keys = re.findall(r'"(img\d+)"', images_block)
        count = len(img_keys)
        
        if count > 0:
            print(f"Updating {t} - replacing {count} images using query '{query}'...")
            new_links = get_pexels_images(query, count)
            
            # Reconstruct the block
            new_block = "{\n"
            for i, key in enumerate(img_keys):
                new_block += f'      "{key}": "{new_links[i]}"'
                if i < len(img_keys) - 1:
                    new_block += ",\n"
                else:
                    new_block += "\n"
            new_block += "    }"
            
            new_content = content[:match.start(1)] + new_block + content[match.end(1):]
            with open(idx_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    else:
        print(f"No PAGE_IMAGES block found in {t}")

print("Done replacing image links!")

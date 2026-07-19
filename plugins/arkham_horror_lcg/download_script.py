# Import necessary libraries
import json
import requests
from urllib import response
import os
from io import BytesIO
from PIL import Image  # For image processing


# Set up directory paths for organizing downloaded card images
current_dir = os.getcwd()
ds_front_dir = os.path.join(current_dir, r'Double Sided\front')
ds_back_dir = os.path.join(current_dir, r'Double Sided\back')
player_front_dir = os.path.join(current_dir, r'Player Cards\front')
campaign_front_dir = os.path.join(current_dir, r'Campaign Cards\front')

# Load card data from JSON file
# Open JSON using UTF-8 to avoid Windows cp1252 decode errors
with open('test.json', 'r', encoding='utf-8') as data_file:              # EDIT THIS LINE FOR JSON IMPORT #
    data = json.load(data_file)
    print(len(data))
    # Iterate through each card in the data
    for v in data:
        # Build URL for the card image
        front_url = 'https://assets.arkham.build/optimized/'
        front_url += v['code'] + '.avif'
        print (front_url)
        i = 0
        
        # Create multiple copies of the card based on quantity
        while (i < v['quantity']):
            front_action_item = requests.get(front_url)  # Download the front image for this copy
            output = ''
            output += v['code'] + str(i) + '.png'
            
            # Check if this is a Mythos (campaign) card
            if ('faction_code' in v) and (v['faction_code'] == 'mythos') and not ('double_sided' in v) and not ('back_link_id' in v):
                with open (os.path.join(campaign_front_dir, output),  "wb") as file:
                    file.write(front_action_item.content)
            
            else:
                # Handle double-sided cards
                if ('double_sided' in v) and v['double_sided']:
                    with open (os.path.join(ds_front_dir, output),  "wb") as file:
                        file.write(front_action_item.content)
                    # Get the back side of the card (code changes from 'a' to 'b' or adds 'b')
                    back_url = 'https://assets.arkham.build/optimized/'
                    if v['code'].endswith('a'):
                        back_url += v['code'][:-1] + 'b.avif'
                    else:
                        back_url += v['code'] + 'b.avif'
                    print (back_url)
                    action_item = requests.get(back_url)
                    try:
                        with Image.open(BytesIO(action_item.content)) as im:
                            im.verify()
                    except Exception:
                        fallback_url = 'https://assets.arkham.build/optimized/' + v['code'] + 'b.avif'
                        print(fallback_url)
                        action_item = requests.get(fallback_url)
                    output = ''
                    output += v['code']+ str(i) + '.png'
                    with open (os.path.join(ds_back_dir, output),  "wb") as file:
                        file.write(action_item.content)
                        
                else:
                    # Handle cards with linked back sides
                    if ('back_link_id' in v):
                        
                        with open (os.path.join(ds_front_dir, output),  "wb") as file:
                            file.write(front_action_item.content)
                            
                        back_url = 'https://assets.arkham.build/optimized/' + v['back_link_id'] + '.avif'
                        print (back_url)
                        action_item = requests.get(back_url)
                        try:
                            with Image.open(BytesIO(action_item.content)) as im:
                                im.verify()
                        except Exception:
                            fallback_url = 'https://assets.arkham.build/optimized/' + v['back_link_id'] + 'b.avif'
                            print(fallback_url)
                            action_item = requests.get(fallback_url)
                        output = ''
                        output += v['code'] + str(i) + '.png'
                        with open (os.path.join(ds_back_dir, output),  "wb") as file:
                            file.write(action_item.content)
                    
                    else:
                        # Save standard player cards
                        with open (os.path.join(player_front_dir, output),  "wb") as file:
                            file.write(front_action_item.content)
                        
            i += 1

# Post-processing: Rotate landscape images to portrait orientation
for (root, dirs, files) in os.walk(os.getcwd()):
    for filename in files:
        if filename.endswith('.png'):
           with Image.open(os.path.join(root, filename)) as im:
                # Check if image is wider than it is tall (landscape)
                if im.width > im.height:
                    # Rotate 90 degrees counter-clockwise for proper card orientation
                    im = im.transpose(Image.ROTATE_90)
                    im.save(os.path.join(root, filename))
                 # Back-side images need to be flipped after the base rotation.
                    if os.path.basename(root).lower() == 'back':
                        im = im.transpose(Image.ROTATE_180)
                        im.save(os.path.join(root, filename))     
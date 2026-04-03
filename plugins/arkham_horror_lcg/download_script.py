# Import necessary libraries
import json
import requests
from urllib import response
import os
from PIL import Image  # For image processing


# Set up directory paths for organizing downloaded card images
current_dir = os.getcwd()
ds_front_dir = os.path.join(current_dir, r'Double Sided\front')
ds_back_dir = os.path.join(current_dir, r'Double Sided\back')
player_front_dir = os.path.join(current_dir, r'Player Cards\front')
campaign_front_dir = os.path.join(current_dir, r'Campaign Cards\front')


# Load card data from JSON file
with open('rcr_cards.json') as data_file:
    data = json.load(data_file)
    print (data.count)
    # Iterate through each card in the data
    for v in data:
        # Build URL for the card image
        url = 'https://assets.arkham.build/optimized/'
        url += v['code'] + '.avif'
        print (url)
        action_item = requests.get(url)  # Download the image
        i = 0
        
        # Create multiple copies of the card based on quantity
        while (i < v['quantity']):
            print(action_item)
            output = ''
            output += v['code'] + str(i) + '.png'
            
            # Check if this is a Mythos (campaign) card
            if ('faction_code' in v) and (v['faction_code'] == 'mythos') and not ('double_sided' in v) and not ('back_link_id' in v):
                with open (os.path.join(campaign_front_dir, output),  "wb") as file:
                    file.write(action_item.content)
            
            else:
                # Handle double-sided cards
                if ('double_sided' in v) and v['double_sided']:
                    with open (os.path.join(ds_front_dir, output),  "wb") as file:
                        file.write(action_item.content)
                    # Get the back side of the card (code changes from 'a' to 'b' or adds 'b')
                    url = 'https://assets.arkham.build/optimized/'
                    if v['code'].endswith('a'):
                        url += v['code'][:-1] + 'b.avif'
                    else:
                        url += v['code'] + 'b.avif'
                    print (url)
                    action_item = requests.get(url)
                    output = ''
                    output += v['code']+ str(i) + '.png'
                    with open (os.path.join(ds_back_dir, output),  "wb") as file:
                        file.write(action_item.content)
                        
                else:
                    # Handle cards with linked back sides
                    if ('back_link_id' in v):
                        
                        with open (os.path.join(ds_front_dir, output),  "wb") as file:
                            file.write(action_item.content)
                            
                        url = 'https://assets.arkham.build/optimized/' + v['back_link_id'] + '.avif'
                        print (url)
                        action_item = requests.get(url)
                        output = ''
                        output += v['code'] + str(i) + '.png'
                        with open (os.path.join(ds_back_dir, output),  "wb") as file:
                            file.write(action_item.content)
                    
                    else:
                        # Save standard player cards
                        with open (os.path.join(player_front_dir, output),  "wb") as file:
                            file.write(action_item.content)
                        
            i += 1
   
# Post-processing: Rotate landscape images to portrait orientation
for (root, dirs, files) in os.walk(os.getcwd()):
    for filename in files:
        if filename.endswith('.png'):
           with Image.open(os.path.join(root, filename)) as im:
                # Check if image is wider than it is tall (landscape)
                if im.width > im.height:
                    # Rotate 90 degrees clockwise for proper card orientation
                    im = im.transpose(Image.ROTATE_90)
                    im.save(os.path.join(root, filename))
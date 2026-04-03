## How to use the script

### 1. Go to https://arkham.build

Open settings cog (top right) -> Backup & Restore -> check "Enable developer mode"

![
]({FD823D9F-5F64-4D4D-81FE-FE18BA39337D}.png)

Make sure to **Save Settings**

### 2. Go to https://arkham.build/browse

On the left, select what sets you are interested in printing. Additionally instead of going to the browse menu, you can just navigate to any deck you like.

Under the search bar, click export. This will download a .json file containing all card information from the filters that you chose.

#### **IMPORTANT:** Do note that there are some inconsistencies with how the the json is laid out via the filters. For example, for the core set, if you select the higher hierarchy "Core" which includes both "Core set" and "Revised Core Set", some cards like Knife will have wrong quantities (number of copies). If you only select "Revised Core Set", this set will feature the correct amount of card copies. This behaviour is not tested with other sets so be advised.

Move the .json file in the same folder with the script and rename it to however you want.

### 3. Edit the download_script.py script as follows:

In line 18, edit with your own .json file's name.

Make sure to respect the folder structure and directory paths as it's laid out after the imports

### 4. Run the script

Make sure you have all the dependencies.

After running the script, everything should download correctly and be organized by folders. The cards are specifically named to be compatible with Alan Cha's SCM project. 

https://alan-cha.github.io/silhouette-card-maker/
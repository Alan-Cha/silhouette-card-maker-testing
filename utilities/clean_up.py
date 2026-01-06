### Clears out the game image directories
import os
import shutil

root_path = 'game'
image_folders = ['front', 'double_sided']

def delete_files():
    i = 0

    for folder_name in image_folders:
        working_path = os.path.join(root_path, folder_name)

        for item in os.listdir(working_path):
            full_path = os.path.join(working_path, item)

            if os.path.basename(full_path) == 'EMPTY.md':
                continue

            if os.path.isfile(full_path):
                os.remove(full_path)
                print(f'Deleted file {full_path}')
                i += 1
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
                print(f'Deleted directory {full_path}')
                i += 1

    print(f'Deleted {i} item{"s" if i != 1 else ""}')
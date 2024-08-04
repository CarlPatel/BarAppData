import os
import requests
import subprocess
import json

# Variables
json_file_path = 'all_drinks.json'  # Reletive path to the JSON file

# Path to your local folder
repo_path = os.getcwd()
commit_message = "Add downloaded images from JSON"

# Function to download an image
def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded and saved to {save_path}")
    else:
        print(f"Failed to download image from {image_url}. Status code: {response.status_code}")

# Load JSON data
with open(json_file_path, 'r') as file:
    drinks_data = json.load(file)

# Download each image and save them to the foldder
for drink in drinks_data:
    image_url = drink.get('imageURL')
    drink_id = drink.get('id')
    if image_url and drink_id:
        image_extension = os.path.splitext(image_url)[1]
        image_name = f"{drink_id}{image_extension}"
        image_path = os.path.join(repo_path, "img/", image_name)
        
        # Download the image
        download_image(image_url, image_path)



os.chdir(repo_path)

# Handle git commands
def run_git_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command {' '.join(command)}: {result.stderr}")
    else:
        print(f"Command {' '.join(command)} executed successfully: {result.stdout}")

# Add, commit, and push changes
run_git_command(["git", "add", "-u"])
run_git_command(["git", "add", "img/."])
run_git_command(["git", "commit", "-m", commit_message])
run_git_command(["git", "push"])

print("Images pushed to GitHub repository")
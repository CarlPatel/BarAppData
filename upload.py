import os
import requests
import subprocess
import json
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Relative path to the JSON file
json_file_path = 'all_drinks.json'

# Path to your local folder
repo_path = os.getcwd()
commit_message = "Update imgs"

# Function to download an image
def download_image(image_url, save_path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises HTTPError if status code is not 200
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logging.info(f"Image downloaded and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download image from {image_url}: {e}")

# Function to process each drink entry
def process_drink(drink):
    image_url = drink.get('imageURL')
    drink_id = drink.get('id')
    if image_url and drink_id:
        image_extension = os.path.splitext(image_url)[1]
        image_name = f"{drink_id}{image_extension}"
        image_path = os.path.join(repo_path, "img", image_name)
        
        # Check if image already exists
        if not os.path.exists(image_path):
            # Download the image if it doesn't exist
            download_image(image_url, image_path)
        else:
            logging.info(f"Image already exists: {image_path}")

# Load JSON data
try:
    with open(json_file_path, 'r') as file:
        drinks_data = json.load(file)
except FileNotFoundError as e:
    logging.error(f"JSON file not found: {json_file_path}")
    exit(1)
except json.JSONDecodeError as e:
    logging.error(f"Error decoding JSON file: {e}")
    exit(1)

# Ensure img/ directory exists
img_dir = os.path.join(repo_path, "img")
os.makedirs(img_dir, exist_ok=True)

# Download images concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(process_drink, drinks_data)

# Function to handle git commands
def run_git_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error running command {' '.join(command)}: {result.stderr}")
    else:
        logging.info(f"Command {' '.join(command)} executed successfully: {result.stdout}")

# Check if we're in a git repository
if not os.path.exists(os.path.join(repo_path, '.git')):
    logging.error(f"Not a git repository: {repo_path}")
    exit(1)

# Change directory to the repository path
os.chdir(repo_path)

# Add, commit, and push changes
run_git_command(["git", "add", "-u"])
run_git_command(["git", "add", "img/."])
run_git_command(["git", "commit", "-m", commit_message])
run_git_command(["git", "push"])

logging.info("All images pushed to GitHub repository")
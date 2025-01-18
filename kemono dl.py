import os
import requests
import aiohttp
import asyncio
import urllib.parse
from pathlib import Path
from tqdm import tqdm
import concurrent.futures
import importlib
import sys
import subprocess

# List of required libraries
required_libraries = ['requests', 'tqdm', 'concurrent.futures', 'aiohttp']

# Function to check and install missing libraries
def check_and_install_libraries(libraries):
    for lib in libraries:
        if importlib.util.find_spec(lib) is None:
            print(f"{lib} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

check_and_install_libraries(required_libraries)

# Mapping of platforms to their respective API endpoints
platform_api_endpoints = {
    'fanbox': 'https://kemono.su/api/v1/fanbox/user/{user_id}',
    'patreon': 'https://kemono.su/api/v1/patreon/user/{user_id}',
    'pixiv': 'https://kemono.su/api/v1/pixiv/user/{user_id}',
    'discord': 'https://kemono.su/api/v1/discord/user/{user_id}',
    'fantia': 'https://kemono.su/api/v1/fantia/user/{user_id}',
    'afdian': 'https://kemono.su/api/v1/afdian/user/{user_id}',
    'boosty': 'https://kemono.su/api/v1/boosty/user/{user_id}',
    'gumroad': 'https://kemono.su/api/v1/gumroad/user/{user_id}',
    'subscribestar': 'https://kemono.su/api/v1/subscribestar/user/{user_id}'
}

# Media file formats (images, videos, gifs, etc.)
media_file_extensions = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heif', '.heic',  # Image formats
    '.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg',  # Video formats
    '.ogv', '.3gp',  # Other video formats
    '.apng', '.gifv', '.m4v'  # Animated Image/Video formats
}

async def fetch_artist_data(artist_url):
    parsed_url = urllib.parse.urlparse(artist_url)
    path_segments = parsed_url.path.split('/')
    if len(path_segments) > 1 and path_segments[1] in platform_api_endpoints:
        platform = path_segments[1]
    else:
        print("Invalid URL format or unsupported platform.")
        return None
    platform = parsed_url.path.split('/')[1]
    user_id = parsed_url.path.split('/')[-1]

    # Ensure platform is valid
    if platform not in platform_api_endpoints:
        print("Unsupported platform. Please provide a valid URL.")
        return None

    # Fetch all pages of data
    artist_data = []
    offset = 0
    total_pages = 0
    print("Loading pages...")

    # First, calculate the total number of pages (for progress bar)
    async with aiohttp.ClientSession() as session:
        while True:
            api_url = f"https://kemono.su/api/v1/{platform}/user/{user_id}?o={offset}"
            headers = {'accept': 'application/json'}
            
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    page_data = await response.json()
                    if not page_data:  # No more data
                        break
                    total_pages += 1
                    offset += 50  # Move to the next page
                else:
                    print(f"Failed to fetch data from {platform.capitalize()} API. Status code: {response.status}")
                    break

    # Create a progress bar for page loading
    with tqdm(total=total_pages, desc="Loading pages", ncols=100) as page_bar:
        offset = 0
        async with aiohttp.ClientSession() as session:
            while True:
                api_url = f"https://kemono.su/api/v1/{platform}/user/{user_id}?o={offset}"
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        page_data = await response.json()
                        if not page_data:  # No more data
                            break
                        artist_data.extend(page_data)
                        offset += 50  # Move to the next page
                        page_bar.update(1)
                    else:
                        print(f"Failed to fetch data from {platform.capitalize()} API. Status code: {response.status}")
                        break
    return artist_data

def download_file(file_url, file_name, download_dir, progress_bar):
    try:
        # Get file size for progress bar
        file_size = int(requests.head(file_url).headers.get("Content-Length", 0))
    except KeyError:
        print(f"Failed to get file size for {file_name}")
        return

    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(download_dir, file_name), 'wb') as f:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name, ncols=100, position=1, leave=False) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
                progress_bar.update(1)

def is_media_file(file_name, download_all):
    return download_all or any(file_name.lower().endswith(ext) for ext in media_file_extensions)

def download_media_files(artist_data, download_dir, download_all):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Prepare media download files and calculate total number of files
    total_files = 0
    for post in artist_data:
        if 'attachments' in post:
            for attachment in post['attachments']:
                file_name = attachment['name']
                # Check if the file is a media file based on its extension
                if is_media_file(file_name, download_all):
                    total_files += 1

    # Create a single total progress bar for all downloads (this is what you're asking for)
    with tqdm(total=total_files, desc="Downloading media", ncols=100) as progress_bar:
        # Create a ThreadPoolExecutor with 5 concurrent threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for post in artist_data:
                if 'attachments' in post:
                    for attachment in post['attachments']:
                        file_name = attachment['name']
                        file_url = attachment['path']
                        # Ensure the URL has a scheme
                        if not urllib.parse.urlparse(file_url).scheme:
                            file_url = f"https://kemono.su{file_url}"
                        # Skip thumbnails and zip files, unless downloading everything
                        if should_download_file(file_name, download_all):
                            futures.append(executor.submit(download_file, file_url, file_name, download_dir, progress_bar))

            # Wait for all futures (downloads) to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Exception occurred: {e}")

def should_download_file(file_name, download_all):
    if download_all:
        return True
    if file_name.endswith('.zip') or '_thumb' in file_name:
        return False
    return any(file_name.lower().endswith(ext) for ext in media_file_extensions)

def main():
    artist_url = input("Enter the artist page URL: ").strip()

    # Ask if the user wants to download everything or just media files
    download_option = input("Do you want to download (1) everything or (2) just media files? (Enter 1 or 2): ").strip()

    # Validate download option input
    while download_option not in ['1', '2']:
        print("Invalid input. Please enter 1 or 2.")
        download_option = input("Do you want to download (1) everything or (2) just media files? (Enter 1 or 2): ").strip()

    # Fetch artist data from respective platform API
    artist_data = asyncio.run(fetch_artist_data(artist_url))

    if artist_data:
        # Prompt user to choose download directory
        while True:
            download_dir = input("Enter the directory where you want to download the files: ").strip()
            if os.path.isdir(download_dir) and os.access(download_dir, os.W_OK):
                break
            else:
                print("Invalid directory or no write permission. Please enter a valid directory.")

        # Download media files concurrently
        download_media_files(artist_data, download_dir, download_option == '1')
        print("Download completed!")
    else:
        print("Failed to fetch artist data. Please check the provided URL and try again.")

if __name__ == "__main__":
    main()

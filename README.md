![image](https://kemono.su/static/kemono-logo.svg)

# Bulk Media Downloader for Kemono.su

Welcome to the Bulk Media Downloader for Kemono.su! This Python script simplifies the process of fetching and downloading media files from various content platforms supported by the Kemono.su API. It offers efficient concurrent downloads and robust support for multiple platforms.

---

## Features

- **Fetch Artist Data**: Access content from platforms like Patreon, Fanbox, Pixiv, Discord, Fantia, Afdian, Boosty, Gumroad, and Subscribestar through the Kemono.su API.
- **Concurrent Downloads**: Utilize multiple threads to accelerate the downloading process.
- **Progress Tracking**: Monitor download progress for each file with a clear interface.
- **Error Handling**: Encounter issues? The script will display appropriate error messages for troubleshooting.

---

## Supported Platforms

- Patreon
- Fanbox
- Pixiv
- Discord
- Fantia
- Afdian
- Boosty
- Gumroad
- Subscribestar

---

## Requirements

Ensure Python is installed on your system. This script depends on the following libraries:

- `requests`: For HTTP requests.
- `tqdm`: To display progress bars.
- `concurrent.futures`: For handling multithreaded downloads.

Install these dependencies using pip:

```bash
pip install requests tqdm
```

---

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/V1SIONUSE/Kemono.su-Downloader.git
   cd Kemono.su-Downloader
   ```

2. **Install Dependencies**:

   ```bash
   pip install requests tqdm
   ```

---

## Usage

Run the script with Python:

```bash
python "kemono dl.py"
```

Follow the prompts:

1. **Provide Artist Page URL**:  
   Enter the URL of the artist's page from a supported platform. Examples:
   - `https://kemono.su/patreon/user/2430075`
   - `https://kemono.su/fanbox/user/23216574`

2. **Specify Download Directory**:  
   Define the folder where you want media files saved.

The script will handle fetching and downloading the media files concurrently.

---

## Example Run

### Input

```plaintext
Enter the artist page URL: https://kemono.su/patreon/user/2430075
Enter the directory where you want to download the files: ./downloads
```

### Output

The script will:

- Retrieve media data from the artist's page.
- Download the files to the specified directory while displaying progress.

---

## Notes

- **Thumbnails & Zip Files**: These file types are skipped to focus on relevant media.
- **File Size**: HTTP headers are used to detect file sizes for accurate progress tracking.
- **Platform Compatibility**: Ensure URLs belong to supported platforms.
- **Error Handling**: Errors during fetching or downloading are clearly logged.

---

## Troubleshooting

- **Platform Support**: Verify the artist page URL matches a supported platform.
- **Directory Issues**: Ensure the target folder exists, is writable, and has enough space.

---

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request.

For major features or changes, please open an issue first to discuss your ideas.

---

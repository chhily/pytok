# TikTok Video Downloader

A simple GUI tool to download all videos from a public TikTok profile.

## Features
- Fetches all video URLs from a TikTok user profile
- Downloads videos using yt-dlp
- Simple Tkinter GUI

## Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install [yt-dlp](https://github.com/yt-dlp/yt-dlp) if not already installed:**
   ```bash
   pip install yt-dlp
   ```
4. **(Optional) Install Chrome if not present.**

## Usage

Run the GUI:
```bash
python -m pytok.gui
```

- Enter the TikTok username (without @)
- Click "Download All Videos"
- Videos will be saved in the `downloads/` folder

## Notes
- Only works for public profiles
- Requires Chrome browser installed
- Downloads are saved in the `downloads/` directory 
# Video Downloader for RaiPlay.com 🎬

## Overview 📚

This Python script is designed to download streamed videos from RaiPlay.com by interacting with the M3U8 master file. M3U8 is a playlist file format commonly used for streaming videos over the internet. The script parses the M3U8 master file, extracts video URLs, and provides options to download the video in desired quality and audio format. Additionally, it merges separate video and audio files into a single video file if necessary.

## Prerequisites 🛠️

Before using this script, make sure you have the following prerequisites installed:

- Python 3
- Required Python packages: `requests`, `m3u8`, `selenium`, `webdriver-manager`, `os`, `re`, `moviepy`

You can install the required packages using the following command:

```bash
pip install requests m3u8 selenium webdriver-manager moviepy
```

## Usage 🚀

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/raiplay-downloader.git
   ```

2. Change into the project directory:

   ```bash
   cd raiplay-downloader
   ```

3. Run the script:

   ```bash
   python main.py 
   ```

4. The script prompts you for the RaiPlay.com video link, video quality, and audio selection. It then proceeds to download the video segments and combines them to create the final video file.

## Disclaimer ⚠️

This script is created solely for educational purposes and personal use. Downloading and distributing copyrighted content without permission is generally considered illegal. Be aware of and comply with the terms of service of the specific website and copyright laws in your region, as they may vary.
The developers are not responsible for any misuse of this script.

Future Updates 🌐
The script may support additional websites in future versions. Stay tuned for updates!

Feel free to contribute, report issues, or suggest improvements! 🚀👩‍💻🔧

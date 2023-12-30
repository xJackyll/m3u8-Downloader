# Video Downloader from M3U8 Master File

## Overview

This Python script allows you to download a video from any site using his M3U8 master file. M3U8 is a playlist file format used for streaming videos over the internet. This script parses the M3U8 master file, extracts the video URLs, and downloads the video in segments, combining them to create the final video file.

## Prerequisites

Before using this script, ensure you have the following prerequisites installed:

- Python 3
- Required Python packages: `requests`, `m3u8`

You can install the required packages using the following command:

```bash
pip install requests m3u8
```

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/xJackyll/m3u8-Downloader.git
   ```

2. Change into the project directory:

   ```bash
   cd m3u8-Downloader
   ```

3. Run the script:

   ```bash
   python main.py 
   ```


4. The script ask you the url and the resolution you want and it will download the video segments and combine them to create the final video file.


## Disclaimer

This script is provided for educational and personal use only. Ensure that you have the right to download and store the video content before using this script. The developers are not responsible for any misuse of this script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Feel free to contribute, report issues, or suggest improvements!

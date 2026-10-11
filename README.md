# ⚡ TC Smart Video Loop Generator

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://ko-fi.com/drtancheng)
[![Live Landing Page](https://img.shields.io/badge/Landing_Page-39fdc0?style=for-the-badge&logo=github&logoColor=black)](https://drtancheng.github.io/videolooper/)

Transform short video clips into **flawlessly seamless, ultra-long infinite loops** in seconds! Powered by selective FFmpeg re-encoding for ultra-fast render speeds.

<p align="center">
  <img src="interface.jpg" alt="TC Smart Video Loop Generator Interface" width="800" style="border-radius: 8px;">
</p>

## ✨ Features
- **Seamless Crossfades:** Customizable video and audio crossfades.
- **Fast Rendering:** Re-encodes only boundary transition tiles, leaving intermediate frames untouched.
- **Click-Free Audio:** Rebuilds continuous audio streams without clicks or pops.

## 🎬 Sample Video Output
Check out this 6-hour relaxing music video generated using this app. See if you can spot the seamless loop boundary around **3:59**!

[![Sample Video Output](https://img.youtube.com/vi/QgjzTieuEnc/maxresdefault.jpg)](https://youtu.be/QgjzTieuEnc "TC Smart Video Loop Generator Sample Output")
*💡 Click image above to watch on YouTube (Smooth visual crossfade + zero audio clicks at transition tiles).*

---

## 📋 Prerequisites

Before running the application, make sure your environment includes:

- **Python 3.8+**
- **FFmpeg & FFprobe** installed and added to your system `PATH`

---

## ⚙️ FFmpeg Installation Guide

The app relies on `ffmpeg` and `ffprobe` for video processing and media analysis[cite: 1].

### Windows
1. Download a pre-built build from [ffmpeg.org](https://ffmpeg.org/download.html) or [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. Extract the ZIP file to a folder (e.g., `C:\ffmpeg`).
3. Add the `C:\ffmpeg\bin` directory to your System **Environment Variables** $\rightarrow$ `PATH`.
4. *Alternative via Winget:*
   ```cmd
   winget install FFmpeg


### Note for Malaysian supporters 🇲🇾

For supporters in Malaysia: Should you wish to support our initiative through a local funds transfer, the DuitNow QR code below is available for your convenience.

<p align="left">
  <img src="QR.jpg" alt="DuitNow QR Support" width="220" style="border-radius: 8px;">
</p>

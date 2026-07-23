# videolooper
Blazing-fast Python/Tkinter app for generating seamless, infinite video loops using smart selective FFmpeg encoding &amp; sub-second transition tiles.

# ⚡ TC Smart Video Loop Generator

Transform short video clips into **flawlessly seamless, ultra-long infinite loops** in seconds! 

**TC Smart Video Loop Generator** is a modern desktop application built with Python and Tkinter. Powered by intelligent **selective FFmpeg re-encoding**, it renders only the tiny transition overlap boundaries—stitching multi-hour looping videos together losslessly at **up to 100x render speeds** without quality degradation.

---

## ✨ Features

- 🌀 **Seamless Crossfade Engine:** Seamlessly bridge video loop boundaries with customizable video and audio crossfades.
- 🎨 **Cinematic Transition FX:** Support for built-in dynamic transitions including `fade`, `dissolve`, `wipeleft`, `wiperight`, `slideup`, `slidedown`, and `circleopen`.
- ⚡ **100x Smart Render Strategy:** Bypasses full-video re-encoding by generating small transition tiles and stream-copy stitching the loop blocks losslessly.
- 🎧 **Continuous Audio Track:** Rebuilds underlying audio into a single continuous stream, eliminating loop-boundary clicks and pops.
- 🎯 **Dual Looping Strategies:** Choose between **Precise Duration** (truncates with a custom ending fade-out) or **Perfect Match Loop Limit** (exact loop cycles without truncation).
- 💾 **Smart Disk Space Check:** Built-in working directory selector with live free disk space detection.
- 🖥️ **Modern Dark Mode UI:** Clean, modern desktop terminal interface with live logging, sub-step progress tracking, and process abort control.

---

## 📋 Prerequisites

To run this app, you will need:

1. **Python 3.8+** installed on your system.
2. **FFmpeg & FFprobe** binaries installed and accessible in your system's `PATH`[cite: 1].

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

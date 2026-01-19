<div align="center">

# 🔒 Avert

### AI-Powered Privacy Guardian

**Stop fumbling for your mouse when someone walks in.**  
Avert locks your screen the instant you look away.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![GitHub issues](https://img.shields.io/github/issues/AutoTasksAI/avert)](https://github.com/AutoTasksAI/avert/issues)
[![GitHub stars](https://img.shields.io/github/stars/AutoTasksAI/avert?style=social)](https://github.com/AutoTasksAI/avert/stargazers)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue)](https://getavert.app)


[Download Free](https://getavert.app) • [Get Pro](https://getavert.app) • [Report Issue](https://github.com/AutoTasksAI/avert/issues)

</div>

![Avert Demo](Avert_demo.gif)

---

## 🎯 What is Avert?

Avert is the world's first AI-powered screen privacy tool that watches your back—literally. Using real-time face detection, it instantly locks your screen when you look away or someone approaches.

**Perfect for:**
- 🪙 **Crypto traders** checking wallets in coffee shops
- ✈️ **Digital nomads** working in airports and public spaces  
- 💼 **Remote workers** protecting sensitive client data
- 🎮 **Gamers** securing login credentials between matches

## ✨ Features

### Core (Free & Open Source)
- ⚡ **Real-time face detection** using OpenCV
- 🔒 **Instant screen lock** when you look away
- 🔐 **100% offline** - no cloud, no internet required
- 🛡️ **Privacy-first** - no data leaves your machine
- 🔥 **Firewall-friendly** - works completely offline

### Pro Features ([Available Here](https://getavert.app))
- ⚡ **Hyper-fast 0.5s reaction** time (2x faster)
- 🖼️ **Custom decoy screens** (upload spreadsheets, code, Zoom calls)
- ⚙️ **Advanced settings** and sensitivity controls
- 🔄 **Lifetime updates** included

## 🚀 How It Works

```
1. Your webcam watches for your face (locally, in RAM)
   ↓
2. Avert detects when you look away or someone approaches
   ↓  
3. Your screen instantly locks to a safe mode (black screen or custom decoy)
```

**Technical Stack:**
- OpenCV for face detection
- Real-time processing (<100ms latency)
- Zero network calls
- 100% local operation

## 📥 Installation

### Quick Start (Free Version)

1. Download from [getavert.app](https://getavert.app)
2. Run the installer (Windows 10/11)
3. Allow webcam access
4. You're protected!

5. ### 🛠️ For Developers

Want to contribute or run from source?

```bash
# Clone the repository
git clone https://github.com/AutoTasksAI/avert.git
cd avert

# Install dependencies
pip install -r requirements.txt

# Run the free version
python avert_free.py

# Test your camera (optional)
python test_camera.py
```

**Requirements:**
- Python 3.8 or higher
- Webcam access
- Windows 10/11 (for screen locking functionality)

**Project Structure:**
```
avert/
├── avert_free.py              # Main application (free version)
├── test_camera.py             # Camera testing utility
├── requirements.txt           # Python dependencies
├── haarcascade_*.xml          # OpenCV face detection models
├── decoy.jpg                  # Default decoy screen image
└── avert_logo.png             # Application logo
```

## 🔐 Security & Privacy

**Avert is designed for paranoia:**
- ✅ All processing happens locally in RAM
- ✅ No video is ever saved to disk
- ✅ No internet connection required
- ✅ No telemetry or analytics
- ✅ Open source for full auditability

**Security researchers:** See [SECURITY.md](SECURITY.md) for audit guidelines.

## 🌟 Why Open Source?

We believe privacy tools should be:
1. **Transparent** - You can audit every line of code
2. **Trustworthy** - No hidden data collection
3. **Community-driven** - Improved by security experts worldwide
4. **Educational** - Learn from real-world computer vision

**Business Model:**  
The core protection is free and open source. We offer [Pro features](https://getavert.app) (custom decoys, faster reaction) as a one-time purchase to sustain development.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

Apache License 2.0 - see [LICENSE](LICENSE)

## 📞 Contact

- **Website:** [getavert.app](https://getavert.app)
- **Email:** support@getavert.app
- **Issues:** [GitHub Issues](https://github.com/AutoTasksAI/avert/issues)

---

<div align="center">

**Made with 🔒 for privacy-conscious humans**

[Download](https://getavert.app) • [Get Pro]( https://getavert.app) • [Contribute](CONTRIBUTING.md)

</div>

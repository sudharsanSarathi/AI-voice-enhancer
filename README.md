# 🎵 Voice Enhancer AI

A clean, minimal web application for AI-powered voice enhancement using ClearerVoice models. Remove background noise from audio files with different intensity levels using an intuitive slider interface.

![Voice Enhancer AI](https://img.shields.io/badge/Voice-Enhancer-blue) ![AI-Powered](https://img.shields.io/badge/AI-Powered-green) ![Web-App](https://img.shields.io/badge/Web-App-orange)

## ✨ Features

- **Interactive Slider Interface**: 1-10 intensity scale for precise noise removal control
- **Multiple Audio Formats**: Supports MP3, WAV, FLAC, OGG, AAC, AIFF
- **Three AI Models**: Light, Medium, and Strong enhancement levels
- **Real-time Processing**: Live audio comparison and download
- **Advanced AI Models**: Uses state-of-the-art ClearerVoice models
- **File Size Limit**: Up to 50MB audio files
- **Cross-Platform**: Works on any modern web browser
- **Docker Ready**: Easy deployment with containerization

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio format conversion)
- At least 8GB RAM (16GB recommended for better performance)
- At least 10GB free disk space (for model storage)

### Installation

1. **Clone or download this project**
   ```bash
   git clone https://github.com/sudharsanSarathi/AI-voice-enhancer.git
   cd AI-voice-enhancer
   ```

2. **Download AI Model Files (Important!):**
   
   The AI model checkpoint files are large (>100MB) and are not included in the repository. You need to download them separately:
   
   ```bash
   # The models will be automatically downloaded when you first run the application
   # OR you can manually download them from the ClearerVoice-Studio repository
   ```
   
   **Note**: On first run, the application will automatically download the required model files (~2-5GB total). This may take several minutes depending on your internet connection.

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg (required for audio processing):**

   **macOS:**
   ```bash
   brew install ffmpeg
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **Windows:**
   Download from [FFmpeg official website](https://ffmpeg.org/download.html)

5. **Run the application:**
   ```bash
   python run.py
   ```

6. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## 🎯 How to Use

1. **Upload Audio**: Drag & drop or click to select an audio file
2. **Choose Intensity**: Use the slider to select enhancement level (1-10)
   - **1-3**: Light cleaning (FRCRN_SE_16K) - Fast processing
   - **4-7**: Medium cleaning (MossFormer2_SE_48K) - Balanced quality
   - **8-10**: Strong cleaning (MossFormerGAN_SE_16K) - Best quality
3. **Process**: Click "Generate Enhanced Audio"
4. **Compare & Download**: Listen to both original and enhanced versions, then download

## 🧠 AI Models Used

This application uses the following ClearerVoice models:

| Intensity Range | Model | Description | Processing Speed |
|----------------|-------|-------------|------------------|
| 1-3 (Light) | FRCRN_SE_16K | Fast, lightweight processing | Fast |
| 4-7 (Medium) | MossFormer2_SE_48K | Balanced quality and speed | Medium |
| 8-10 (Strong) | MossFormerGAN_SE_16K | Best quality, more aggressive | Slower |

**Model Performance (from ClearerVoice benchmarks):**
- **PESQ Scores**: 2.94-3.57 (higher is better)
- **STOI Scores**: 0.95-0.98 (higher is better)
- **SISDR Scores**: 17.75-20.60 dB (higher is better)

## 📁 Project Structure

```
voice-enhancer-ai/
├── frontend/
│   └── index.html          # Main web interface with slider
├── backend/
│   └── app.py             # Flask application
├── static/
│   ├── css/
│   │   └── style.css      # Styling with slider design
│   └── js/
│       └── app.js         # Frontend JavaScript with slider logic
├── uploads/               # Uploaded audio files
├── processed/            # Enhanced audio files
├── checkpoints/          # AI model files (downloaded separately)
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── run.py              # Startup script
├── Dockerfile          # Docker configuration
├── render.yaml         # Render deployment config
└── README.md           # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
class Config:
    PORT = 5000                    # Server port
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # Max file size (50MB)
    UPLOAD_FOLDER = Path('uploads')         # Upload directory
    PROCESSED_FOLDER = Path('processed')    # Output directory
```

## 🌐 Deployment Options

### Option 1: Local Deployment (Recommended for Development)

**Pros:**
- Full control over data and processing
- No internet dependency during processing
- Better privacy and security

**Cons:**
- Requires powerful local hardware
- Initial model download (2-5GB)
- Slower on lower-end hardware

**System Requirements:**
- **Minimum**: 8GB RAM, 4-core CPU, 10GB storage
- **Recommended**: 16GB RAM, 6-core CPU, 20GB SSD storage
- **GPU**: Optional but recommended (NVIDIA GPU with CUDA)

### Option 2: Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t voice-enhancer-ai .

# Run the container
docker run -p 5000:5000 voice-enhancer-ai
```

### Option 3: Cloud Deployment (Render.com)

This project is configured for easy deployment on Render.com:

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service
4. Select this repository
5. Render will automatically detect the `render.yaml` configuration
6. Deploy!

**Other Cloud Options:**

#### AWS EC2
```bash
# Instance recommendations:
# - g4dn.xlarge (with GPU): ~$0.71/hour
# - c5.2xlarge (CPU only): ~$0.34/hour
```

#### Google Cloud Platform
```bash
# Instance recommendations:
# - n1-standard-4: ~$0.19/hour
# - n1-highmem-4: ~$0.25/hour (more RAM)
```

## 🔧 Troubleshooting

### Common Issues

1. **"ClearerVoice not available"**
   ```bash
   pip install clearvoice
   ```

2. **"FFmpeg not found"**
   - Install FFmpeg for your system
   - Add FFmpeg to system PATH

3. **"Model download failed"**
   - Check internet connection
   - Models are downloaded from HuggingFace automatically
   - Manual download: Visit [ModelScope](https://modelscope.cn/models/iic/ClearerVoice-Studio/summary)

4. **"File too large"**
   - Increase `MAX_CONTENT_LENGTH` in `config.py`
   - Ensure sufficient disk space

5. **"Processing failed"**
   - Check audio file format compatibility
   - Ensure audio file is not corrupted
   - Try different intensity level

### Performance Tips

- **Use GPU**: Install CUDA and PyTorch with GPU support for faster processing
- **RAM**: More RAM allows processing longer audio files
- **Storage**: SSD storage significantly improves model loading times
- **Light Intensity**: Use for quick processing of shorter files
- **Batch Processing**: Process multiple files in sequence for efficiency

## 📊 API Endpoints

- `GET /` - Main application interface
- `POST /api/process` - Process audio file
- `GET /api/audio/uploads/<filename>` - Get uploaded audio
- `GET /api/audio/processed/<filename>` - Get processed audio
- `GET /api/download/<filename>` - Download processed audio
- `GET /api/health` - Health check

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project uses the ClearerVoice models. Please refer to the [ClearerVoice-Studio repository](https://github.com/modelscope/ClearerVoice-Studio) for licensing information.

## 🙏 Acknowledgments

- **ClearerVoice Team**: For the excellent AI models
- **ModelScope**: For hosting the models
- **HuggingFace**: For model distribution
- **Flask**: For the web framework

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the browser console for errors
3. Check server logs for backend errors
4. Ensure all dependencies are installed correctly

---

**Made with ❤️ for clean, enhanced audio experiences**
# 🎬 AI-Powered LipSync Video Generator

A comprehensive web application that combines multiple AI services to create professional lipsync videos, generate content, translate text, and transcribe audio. Built with Flask and integrated with AWS services and Gooey.ai for advanced AI capabilities.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Transcribe%20%7C%20Translate-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### Core AI Services
- **🎬 LipSync Video Generation**: Create professional lipsync videos using Gooey.ai
  - Text-to-speech with face image
  - Audio file upload with face synchronization
  - Multiple output formats supported

- **🤖 AI Content Generation**: Powered by DeepSeek R1 via AWS Bedrock
  - Advanced reasoning capabilities
  - Creative content generation
  - Script writing and ideation

- **🌍 Multi-Language Translation**: AWS Translate integration
  - Support for 8+ languages (Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese)
  - Real-time translation with fallback support

- **🎵 Audio Transcription**: AWS Transcribe integration
  - Convert audio files to text
  - Multiple audio format support (MP3, WAV, M4A, AAC, OGG, FLAC)
  - Automatic language detection

### Technical Features
- **Modern Web Interface**: Glassmorphism design with responsive layout
- **Multi-Region AWS Support**: Automatic fallback between regions
- **Environment-Based Configuration**: Secure credential management
- **Real-time Processing**: Asynchronous file handling and progress tracking
- **Error Handling**: Comprehensive error management with user-friendly messages

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **boto3**: AWS SDK for Python
- **requests**: HTTP client for external APIs
- **python-multipart**: File upload handling

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Glassmorphism design with animations
- **Vanilla JavaScript**: Async/await for API communication
- **Google Fonts**: Professional typography (Inter family)

### Cloud Services
- **AWS Bedrock**: AI model hosting (DeepSeek R1, Nova, Claude, Llama)
- **AWS Transcribe**: Speech-to-text service
- **AWS Translate**: Text translation service
- **AWS S3**: File storage and management
- **Gooey.ai**: LipSync video generation

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Windows, macOS, or Linux
- 4GB RAM minimum (8GB recommended)
- Internet connection for cloud services

### Required Accounts
1. **AWS Account** with appropriate permissions:
   - Bedrock access (for AI models)
   - Transcribe access
   - Translate access
   - S3 access
2. **Gooey.ai Account** with API access

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-lipsync-generator.git
cd ai-lipsync-generator
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. AWS Configuration

#### Option A: AWS CLI Configuration (Recommended)
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter default output format: json
```

#### Option B: Environment Variables
Create a `.env` file in the project root:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
```

#### Option C: IAM Role (for EC2 deployment)
If deploying on EC2, attach an IAM role with the following permissions:
- `AmazonBedrockFullAccess`
- `AmazonTranscribeFullAccess`
- `AmazonTranslateFullAccess`
- `AmazonS3FullAccess`

### 2. Gooey.ai API Configuration
```env
GOOEY_API_KEY=your_gooey_api_key_here
```

### 3. AWS Bedrock Model Access
Request access to required models in AWS Console:
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to:
   - DeepSeek models
   - Amazon Nova models
   - Anthropic Claude models
   - Meta Llama models

## 🚀 Deployment

### Local Development
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the application
python app.py

# Access at http://localhost:5000
```

### Production Deployment

#### Option 1: AWS EC2
1. Launch EC2 instance (Ubuntu 20.04 LTS recommended)
2. Install Python 3.8+ and pip
3. Clone repository and follow installation steps
4. Install nginx and configure reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. Use systemd for process management:
```ini
[Unit]
Description=AI LipSync Generator
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-lipsync-generator
Environment=PATH=/home/ubuntu/ai-lipsync-generator/venv/bin
ExecStart=/home/ubuntu/ai-lipsync-generator/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Option 2: Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

```bash
docker build -t ai-lipsync-generator .
docker run -p 5000:5000 --env-file .env ai-lipsync-generator
```

#### Option 3: Heroku Deployment
1. Create `Procfile`:
```
web: python app.py
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set AWS_ACCESS_KEY_ID=your_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
heroku config:set GOOEY_API_KEY=your_gooey_key
git push heroku main
```

## 📖 Usage Guide

### 1. AI Content Generation
1. Navigate to the "AI Content Generation" section
2. Enter your prompt (e.g., "Create a 30-second space exploration script")
3. Click "Generate Content"
4. Copy the generated content for use in other sections

### 2. Text Translation
1. Go to the "Translation" section
2. Enter text to translate
3. Select target language
4. Click "Translate"
5. Use translated text in your projects

### 3. Audio Transcription
1. Access the "Audio Transcription" section
2. Upload an audio file (MP3, WAV, etc.)
3. Click "Transcribe"
4. Copy the transcribed text

### 4. LipSync Video Generation
1. Choose your input method:
   - **Text-to-Speech**: Enter text and upload face image
   - **Audio Upload**: Upload audio file and optionally a face image
2. Enter your Gooey.ai API key
3. Click "Generate LipSync Video"
4. Download the generated video

## 🔒 Security Best Practices

### Credential Management
- ✅ Never commit API keys to version control
- ✅ Use environment variables for sensitive data
- ✅ Rotate API keys regularly
- ✅ Use IAM roles when possible on AWS

### File Security
- ✅ Uploaded files are automatically cleaned up
- ✅ File type validation prevents malicious uploads
- ✅ Size limits prevent resource exhaustion

### Network Security
- ✅ HTTPS recommended for production
- ✅ API rate limiting implemented
- ✅ Input validation on all endpoints

## 🔧 Troubleshooting

### Common Issues

#### AWS Credential Errors
```bash
# Test AWS credentials
aws sts get-caller-identity

# If error, reconfigure
aws configure
```

#### Model Access Denied
1. Go to AWS Bedrock Console
2. Request model access
3. Wait for approval (can take 24-48 hours)

#### Gooey.ai API Errors
1. Verify API key is correct
2. Check account balance
3. Ensure API access is enabled

#### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill
```

### Performance Optimization
- Use smaller audio files for faster processing
- Optimize images before upload
- Consider caching for frequently used translations
- Use CDN for static assets in production

## 📁 Project Structure

```
ai-lipsync-generator/
├── app.py                 # Main Flask application
├── aws_config.py          # AWS region and model configuration
├── aws_helpers.py         # AWS service helper functions
├── aws_helpers_fake.py    # Fallback functions for demo mode
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── .env.example          # Environment variables template
├── static/               # Static web assets
│   ├── style.css         # Modern CSS with glassmorphism
│   └── script.js         # JavaScript for frontend
├── templates/            # HTML templates
│   └── index.html        # Main web interface
├── uploads/              # Temporary file storage
├── docs/                 # Documentation
│   └── AWS_SETUP.md      # AWS setup guide
├── scripts/              # Utility scripts
│   ├── setup_aws.py      # AWS credential setup
│   └── request_nova_access.py  # Nova model access
└── tests/                # Test files
    ├── test_*.py         # Various test scripts
    └── analyze_*.py      # Analysis scripts
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AWS** for providing robust cloud AI services
- **Gooey.ai** for advanced LipSync capabilities
- **DeepSeek** for state-of-the-art reasoning models
- **Flask** community for the excellent web framework

## 🗺️ Roadmap

- [ ] Support for additional video formats
- [ ] Batch processing capabilities
- [ ] WebRTC integration for real-time processing
- [ ] Mobile app version
- [ ] Advanced facial expression controls
- [ ] Integration with more AI providers

---

**Made with ❤️ by changyy06**

*Transform text into engaging lipsync videos with the power of AI*
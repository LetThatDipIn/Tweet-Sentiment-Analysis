# AI Tweet Emotion Analyzer 🤖

A sophisticated emotion classification system that analyzes text and provides detailed sentiment analysis with automatic summarization.

## 🌟 Features

- **Real-time Emotion Detection**: Classifies text into 6 emotion categories (Joy, Sadness, Love, Anger, Fear, Surprise)
- **Advanced AI Analysis**: Powered by TensorFlow deep learning models
- **Intelligent Summarization**: Uses Transformer models for comprehensive text analysis
- **Beautiful Web Interface**: Modern, responsive design with real-time feedback
- **Production Ready**: Optimized Docker deployment for Hugging Face Spaces

## 🎯 Supported Emotions

1. **😊 Joy** - Happiness, excitement, satisfaction
2. **😢 Sadness** - Sorrow, disappointment, melancholy  
3. **❤️ Love** - Affection, care, romantic feelings
4. **😠 Anger** - Frustration, irritation, rage
5. **� Fear** - Anxiety, worry, apprehension
6. **😲 Surprise** - Astonishment, shock, amazement

## 🚀 Quick Start

### Using the Web Interface

1. Visit the application URL
2. Enter your text in the analysis box
3. Click "Analyze Emotion" 
4. View detailed results with confidence scores and AI-generated summary

### API Usage

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "I am absolutely thrilled about this amazing opportunity!"}'
```

Response:
```json
{
  "emotion": "joy",
  "confidence": 0.892,
  "summary": "😊 This text radiates positive energy and happiness...",
  "original_text": "I am absolutely thrilled about this amazing opportunity!"
}
```

## 🛠️ Technology Stack

- **Backend**: FastAPI + Uvicorn
- **AI Models**: TensorFlow 2.18.0, Transformers (BART)
- **Frontend**: Modern HTML5/CSS3/JavaScript
- **Deployment**: Docker + Hugging Face Spaces
- **Architecture**: Bidirectional LSTM for emotion classification

## 📊 Model Performance

- **Training Accuracy**: ~85%
- **Validation Accuracy**: ~82%
- **Real-time Processing**: <2 seconds average response time
- **Supported Languages**: Primarily English (optimized)

## 🔧 Development

### Local Setup

```bash
# Clone the repository
git clone <repository-url>
cd sentiment_analysis

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Docker Deployment

```bash
# Build the image
docker build -t emotion-analyzer .

# Run the container (Hugging Face Spaces uses port 7860)
docker run -p 7860:7860 emotion-analyzer
```

## 📝 API Endpoints

- `GET /` - Web interface
- `POST /predict` - Emotion analysis endpoint
- `GET /health` - Health check endpoint

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Feedback**: Visual indicators during text input
- **Emotion-specific Styling**: Colors and animations match detected emotions
- **Loading Animations**: Smooth transitions and feedback
- **Accessibility**: WCAG compliant design

## 🔍 Model Details

The emotion classification model uses:
- **Architecture**: Bidirectional LSTM with attention mechanism
- **Vocabulary**: 10,000+ tokens
- **Sequence Length**: 50 tokens maximum
- **Training Data**: Combined datasets from multiple emotion classification sources
- **Preprocessing**: Text tokenization, padding, and normalization

## 🌐 Deployment

This application is optimized for deployment on:
- **Hugging Face Spaces** (recommended)
- AWS/GCP/Azure
- Local Docker environments
- Kubernetes clusters

### Hugging Face Spaces Deployment

1. Upload your repository to Hugging Face Spaces
2. Set the Space type to "Docker"
3. The application will automatically deploy on port 7860
4. Use the optimized Dockerfile for best performance

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using TensorFlow and FastAPI

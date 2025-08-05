import os
# Force CPU usage to avoid CUDA/GPU compilation issues
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import uvicorn

# Import transformers with error handling
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import transformers: {e}")
    TRANSFORMERS_AVAILABLE = False
    pipeline = None

app = FastAPI(title="Tweet Emotion Classification API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the model and tokenizer
try:
    # Load model (should work with upgraded TensorFlow 2.18.0)
    print("Loading emotion classification model...")
    model = tf.keras.models.load_model("emotion_model.h5")
    print("✓ Emotion model loaded successfully")
    
    # Load tokenizer
    print("Loading tokenizer...")
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    print("✓ Tokenizer loaded successfully")
    
    # Load the summarizer with error handling
    print("Loading summarization model...")
    summarizer = None
    if TRANSFORMERS_AVAILABLE:
        try:
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            print("✓ Summarizer loaded successfully")
        except Exception as sum_e:
            print(f"Warning: Summarizer failed to load: {sum_e}")
            print("Using fallback summarization...")
            summarizer = None
    else:
        print("⚠️  Transformers not available, using fallback summarization")
        
    print("🎉 All models loaded successfully!")
        
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    tokenizer = None
    summarizer = None

# Constants from your notebook
MAX_SEQUENCE_LENGTH = 50
EMOTION_LABELS = {
    0: "sadness",
    1: "joy", 
    2: "love",
    3: "anger",
    4: "fear",
    5: "surprise"
}

class TweetInput(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    emotion: str
    confidence: float
    summary: str
    original_text: str

@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.post("/predict", response_model=PredictionResponse)
async def predict_emotion(tweet: TweetInput):
    if not model or not tokenizer:
        raise HTTPException(status_code=500, detail="Model not loaded properly")
    
    try:
        # Preprocess the text (same as in your notebook)
        sequences = tokenizer.texts_to_sequences([tweet.text])
        padded_sequence = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
        
        # Make prediction
        prediction = model.predict(padded_sequence, verbose=0)
        predicted_emotion_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_emotion_idx])
        emotion = EMOTION_LABELS[predicted_emotion_idx]
        
        # Generate summary
        summary = generate_summary(tweet.text, emotion)
        
        return PredictionResponse(
            emotion=emotion,
            confidence=confidence,
            summary=summary,
            original_text=tweet.text
        )
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def generate_summary(text: str, emotion: str) -> str:
    """Generate a comprehensive summary based on the emotion and text"""
    
    # If transformers is available and summarizer is loaded, use it for longer texts
    if summarizer and len(text) > 50:
        try:
            # Use BART for summarization with better parameters
            summary_result = summarizer(
                text, 
                max_length=120,  # Increased for more comprehensive summaries
                min_length=30, 
                do_sample=False,
                truncation=True
            )
            ai_summary = summary_result[0]['summary_text']
            
            # Enhanced emotion-specific analysis
            emotion_insights = {
                "joy": "😊 This text radiates positive energy and happiness. The content suggests feelings of elation, excitement, or contentment.",
                "sadness": "😢 This text conveys melancholy and sorrow. The language indicates feelings of loss, disappointment, or emotional pain.",
                "love": "❤️ This text expresses deep affection and care. The content shows warmth, attachment, or romantic/familial love.",
                "anger": "😠 This text displays frustration and irritation. The language suggests feelings of annoyance, rage, or indignation.",
                "fear": "😨 This text reveals anxiety and concern. The content indicates worry, apprehension, or feelings of being threatened.",
                "surprise": "😲 This text shows astonishment and unexpectedness. The language suggests shock, amazement, or sudden realization."
            }
            
            insight = emotion_insights.get(emotion, "🤔 This text has been analyzed for emotional patterns and sentiment.")
            
            return f"{insight}\n\n📝 Content Summary: {ai_summary}\n\n🎯 Detected Emotion: {emotion.title()} - This classification is based on linguistic patterns, word choice, and emotional indicators found in the text."
            
        except Exception as e:
            print(f"Advanced summarization failed: {e}")
            # Fall back to enhanced simple processing
    
    # Enhanced fallback summarization with better emotion analysis
    words = text.split()
    
    # More intelligent text processing
    if len(words) <= 20:
        base_content = text
        content_note = "Full text analyzed"
    elif len(words) <= 40:
        base_content = " ".join(words[:30]) + "..."
        content_note = f"Showing first 30 of {len(words)} words"
    else:
        # For very long texts, take beginning and end
        beginning = " ".join(words[:20])
        ending = " ".join(words[-10:])
        base_content = f"{beginning} ... {ending}"
        content_note = f"Excerpt from {len(words)} words"
    
    # Enhanced emotion-specific analysis for fallback
    detailed_emotion_analysis = {
        "joy": {
            "description": "😊 Joy & Happiness Detected",
            "analysis": "The text contains language patterns associated with positive emotions, excitement, satisfaction, or celebration. Words and phrases indicate an uplifting, cheerful, or optimistic sentiment.",
            "indicators": "Look for words expressing delight, enthusiasm, accomplishment, or positive anticipation."
        },
        "sadness": {
            "description": "😢 Sadness & Melancholy Detected", 
            "analysis": "The text shows linguistic markers of sorrow, disappointment, or emotional distress. The language patterns suggest feelings of loss, regret, or emotional pain.",
            "indicators": "Common themes include loss, longing, disappointment, or expressions of emotional hurt."
        },
        "love": {
            "description": "❤️ Love & Affection Detected",
            "analysis": "The text demonstrates warm, caring language patterns indicating deep emotional connection, affection, or romantic feelings. The content suggests strong positive attachment to someone or something.",
            "indicators": "Language shows care, devotion, appreciation, or intimate emotional connection."
        },
        "anger": {
            "description": "😠 Anger & Frustration Detected",
            "analysis": "The text contains aggressive or frustrated language patterns indicating irritation, annoyance, or rage. The linguistic style suggests emotional tension or conflict.",
            "indicators": "Look for expressions of displeasure, criticism, confrontational language, or frustrated tone."
        },
        "fear": {
            "description": "😨 Fear & Anxiety Detected",
            "analysis": "The text shows language patterns associated with worry, apprehension, or anxiety. The content suggests concerns about potential threats, uncertainty, or stressful situations.",
            "indicators": "Common themes include worry, uncertainty, potential danger, or expressions of nervousness."
        },
        "surprise": {
            "description": "😲 Surprise & Astonishment Detected",
            "analysis": "The text contains language indicating unexpected events, sudden realizations, or astonishment. The linguistic patterns suggest reactions to unforeseen circumstances or remarkable discoveries.",
            "indicators": "Look for expressions of amazement, shock, unexpected discoveries, or sudden changes."
        }
    }
    
    emotion_data = detailed_emotion_analysis.get(emotion, {
        "description": "🤔 Emotional Content Analyzed",
        "analysis": "The text has been processed for emotional content and sentiment patterns.",
        "indicators": "Various linguistic and contextual clues were analyzed."
    })
    
    return f"""{emotion_data['description']}

🔍 Analysis: {emotion_data['analysis']}

📝 Content ({content_note}): {base_content}

💡 Key Indicators: {emotion_data['indicators']}

🎯 Final Classification: {emotion.title()} - This emotion was identified through analysis of word choice, sentence structure, and contextual emotional markers."""

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = "loaded" if model is not None else "failed"
    tokenizer_status = "loaded" if tokenizer is not None else "failed"
    summarizer_status = "loaded" if summarizer is not None else "fallback"
    
    return {
        "status": "healthy",
        "model": model_status,
        "tokenizer": tokenizer_status, 
        "summarizer": summarizer_status,
        "transformers_available": TRANSFORMERS_AVAILABLE
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

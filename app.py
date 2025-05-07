from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import spacy
import re
import numpy as np

app = Flask(__name__)

model = load_model('model_gru.h5')
nlp = spacy.load('en_core_web_sm')
top_words = 6000
max_length = 130
tokenizer = Tokenizer(num_words=top_words)

def preprocessing(text):
    text = re.sub("<[a][^>]*>(.+?)</[a]>", 'Link.', text)
    text = text.lower()
    text = re.sub(r'\S*@\S*\s?', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'\s\s+', ' ', text)
    text = re.sub(r'\n', '', text)

    doc = nlp(text)
    cleaned_tokens = []
    for token in doc:
        if not (token.is_stop or token.is_punct):
            cleaned_tokens.append(token.text)
    return " ".join(cleaned_tokens)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        text = data['text']
        
        cleaned_text = preprocessing(text)
        
        tokenizer.fit_on_texts([cleaned_text])
        sequence = tokenizer.texts_to_sequences([cleaned_text])
        padded_sequence = pad_sequences(sequence, maxlen=max_length)
        
        prediction = model.predict(padded_sequence)[0][0]
        sentiment = 'positive' if prediction > 0.5 else 'negative'
        
        return jsonify({
            'sentiment': sentiment,
            'confidence': float(prediction) * 100
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# OpenRouter API configuration
API_KEY = os.getenv('OPENROUTER_API_KEY', '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')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def encode_pdf_to_base64(pdf_file):
    """Convert PDF file to base64 encoded string"""
    return base64.b64encode(pdf_file.read()).decode('utf-8')

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and process with OpenRouter API"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Encode PDF to base64
        base64_pdf = encode_pdf_to_base64(file)
        data_url = f"data:application/pdf;base64,{base64_pdf}"
        
        # Prepare OpenRouter API request
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please analyze this document and provide a comprehensive summary. Include the main topics, key points, and important details."
                    },
                    {
                        "type": "file",
                        "file": {
                            "filename": file.filename,
                            "file_data": data_url
                        }
                    }
                ]
            }
        ]
        
        # Configure PDF processing
        plugins = [
            {
                "id": "file-parser",
                "pdf": {
                    "engine": "pdf-text"
                }
            }
        ]
        
        payload = {
            "model": "openai/gpt-4o",  # Using GPT-4 as gpt5 is not yet available
            "messages": messages,
            "plugins": plugins
        }
        
        # Make API request
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # Extract the summary from the response
            summary = result.get('choices', [{}])[0].get('message', {}).get('content', 'No summary generated')
            return jsonify({
                'success': True,
                'summary': summary,
                'filename': file.filename
            })
        else:
            return jsonify({
                'error': f'API request failed: {response.status_code}',
                'details': response.text
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


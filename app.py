from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import re
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
                        "text": """Please analyze this document and extract the key concepts, topics, and important information.
                        
Return the result in JSON format as a list of concepts. Each concept should have:
- "title": A concise title for the concept (2-5 words)
- "content": A clear description or explanation of the concept (1-3 sentences)

Format the response as a valid JSON array like this:
[
    {
        "title": "title of the concept",
        "content": "description of the concept"
    },
    {
        "title": "title of the concept",
        "content": "description of the concept"
    }
]

Extract 5-15 key concepts depending on the document length and complexity. Focus on the most important and useful information."""
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
            # Extract the content from the response
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Try to parse the JSON response
            try:
                # The response might have markdown code blocks, so we need to clean it
                import re
                # Remove markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # If no code blocks, try to find JSON array directly
                    json_match = re.search(r'(\[.*\])', content, re.DOTALL)
                    json_str = json_match.group(1) if json_match else content
                
                concepts = json.loads(json_str)
                
                # Save the extracted concepts to pdf2points_example.json
                output_file = os.path.join(os.path.dirname(__file__), 'pdf2points_example.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(concepts, f, ensure_ascii=False, indent=4)
                
                return jsonify({
                    'success': True,
                    'concepts': concepts,
                    'filename': file.filename
                })
            except (json.JSONDecodeError, AttributeError) as e:
                # If parsing fails, return the raw content
                return jsonify({
                    'success': True,
                    'concepts': [],
                    'raw_content': content,
                    'filename': file.filename,
                    'warning': 'Could not parse JSON response'
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


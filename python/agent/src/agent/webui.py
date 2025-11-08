"""
Flask web server for CheatSheet
Provides web UI and API endpoints
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import re
import base64
import os
from .config import config
from .agent import agent


# Initialize Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)
CORS(app)


def encode_pdf_to_base64(pdf_file):
    """Convert PDF file to base64 encoded string"""
    return base64.b64encode(pdf_file.read()).decode('utf-8')


# ============ Web UI Routes ============

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('webui.html')


# ============ PDF Upload API ============

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
            "Authorization": f"Bearer {config.api_key}",
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
            "model": config.llm.model,
            "messages": messages,
            "plugins": plugins
        }
        
        # Make API request
        response = requests.post(config.llm.openrouter_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Try to parse the JSON response
            try:
                # Remove markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # If no code blocks, try to find JSON array directly
                    json_match = re.search(r'(\[.*\])', content, re.DOTALL)
                    json_str = json_match.group(1) if json_match else content
                
                concepts = json.loads(json_str)
                
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


# ============ Course Management API ============

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get list of available courses"""
    try:
        courses = agent.mcp.get_courses()
        return jsonify({'success': True, 'courses': courses})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save_concepts', methods=['POST'])
def save_concepts():
    """Save concepts to database"""
    try:
        data = request.get_json()
        concepts = data.get('concepts', [])
        course_name = data.get('course_name', '')
        
        if not course_name:
            return jsonify({'error': 'Course name is required'}), 400
        
        if not concepts:
            return jsonify({'error': 'No concepts provided'}), 400
        
        # Process concepts using agent
        result = agent.process_uploaded_concepts(concepts, course_name)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ Quiz API ============

@app.route('/api/generate_quizzes', methods=['POST'])
def generate_quizzes():
    """Generate quizzes for the uploaded concepts"""
    try:
        # Handle empty request body gracefully
        data = request.get_json(silent=True) or {}
        num_quizzes = data.get('num_quizzes', 10)
        
        print(f"\n[API] Generating {num_quizzes} quizzes...")
        
        # Generate quizzes using agent
        quizzes = agent.generate_quizzes(num_quizzes=num_quizzes)
        
        print(f"[API] Generated {len(quizzes) if quizzes else 0} quizzes")
        
        if not quizzes:
            print("[API] No concepts found for quiz generation")
            return jsonify({'error': 'No concepts found'}), 404
        
        return jsonify({
            'success': True,
            'quizzes': quizzes,
            'count': len(quizzes)
        })
        
    except Exception as e:
        print(f"\n[ERROR] Failed to generate quizzes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluate_answer', methods=['POST'])
def evaluate_answer():
    """Evaluate user's answer"""
    try:
        data = request.get_json()
        user_answer = data.get('user_answer')
        concept_ref = data.get('concept_ref')
        concept = data.get('concept')
        
        if not user_answer or not concept:
            return jsonify({'error': 'Missing required data'}), 400
        
        # Evaluate using agent
        result = agent.evaluate_quiz_answer(
            user_answer=user_answer,
            correct_answer=None,  # For short answer, LLM will evaluate
            concept_id=concept_ref
        )
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system_prompt', methods=['GET'])
def system_prompt():
    """Get system prompt with resolved knowledge"""
    try:
        prompt_data = agent.mcp.get_system_prompt()
        return jsonify({
            'success': True,
            'prompt_data': prompt_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ Main ============

def run_server():
    """Run the Flask server"""
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    )


if __name__ == '__main__':
    run_server()


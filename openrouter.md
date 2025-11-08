import requests
import json
import base64
from pathlib import Path

def encode_pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY_REF}",
    "Content-Type": "application/json"
}

# Read and encode the PDF
pdf_path = "path/to/your/document.pdf"
base64_pdf = encode_pdf_to_base64(pdf_path)
data_url = f"data:application/pdf;base64,{base64_pdf}"

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "What are the main points in this document?"
            },
            {
                "type": "file",
                "file": {
                    "filename": "document.pdf",
                    "file_data": data_url
                }
            },
        ]
    }
]

# Optional: Configure PDF processing engine
# PDF parsing will still work even if the plugin is not explicitly set
plugins = [
    {
        "id": "file-parser",
        "pdf": {
            "engine": "pdf-text"  # defaults to "mistral-ocr". See Pricing above
        }
    }
]

payload = {
    "model": "google/gemma-3-27b-it",
    "messages": messages,
    "plugins": plugins
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())

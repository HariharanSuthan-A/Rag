from flask import Flask, render_template, request, jsonify
import PyPDF2
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini API - Replace with your actual API key
GEMINI_API_KEY = "AIzaSyD0dSgpqUOXpvToAadhglcFIHrNrvayRFA"  # Replace with your actual key

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Preload the PDF
def load_pdf_text(pdf_path="test.pdf"):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# Load the PDF on startup
pdf_text = load_pdf_text()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    global pdf_text
    
    if not pdf_text:
        return jsonify({'success': False, 'message': 'PDF not loaded properly'})
    
    question = request.form.get('question')
    
    if not question:
        return jsonify({'success': False, 'message': 'Question not provided'})
    
    try:
        # Query Gemini with the question and PDF context
        prompt = f"Based on the following document, please answer this question: {question}\n\nDocument content:\n{pdf_text[:15000]}"  # Limit context length
        response = model.generate_content(prompt)
        answer = response.text
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error querying Gemini API: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
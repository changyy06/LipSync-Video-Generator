from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime
import base64
import tempfile
from aws_helpers import AWSHelper, transcribe_audio_fallback, translate_text_fallback, generate_content_fallback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize AWS helper (with fallback for demo)
try:
    aws_helper = AWSHelper()
    aws_enabled = True
    print("AWS services initialized successfully")
except Exception as e:
    print(f"AWS initialization failed: {e}")
    print("Using fallback demo functions")
    aws_helper = None
    aws_enabled = False

# Allowed file extensions for uploads
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac', 'webm'}

def allowed_file(filename, file_type='image'):
    if file_type == 'image':
        extensions = ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'audio':
        extensions = ALLOWED_AUDIO_EXTENSIONS
    else:
        return False
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions

def upload_file_to_base64(file):
    """Convert file to base64 data URL"""
    try:
        print(f"Converting file to base64: {file.filename}")
        
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Get file extension for MIME type
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        # Determine MIME type
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'webm': 'audio/webm',
            'mp4': 'audio/mp4',
            'm4a': 'audio/mp4',
            'aac': 'audio/aac',
            'ogg': 'audio/ogg',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        
        mime_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # Convert to base64
        base64_content = base64.b64encode(file_content).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_content}"
        
        print(f"File converted to base64 data URL (size: {len(data_url)} chars)")
        return data_url
        
    except Exception as e:
        print(f"Error converting file to base64: {e}")
        raise e

def download_video(video_url, api_key):
    """Download video from URL and save to Downloads folder"""
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lipsync_video_{timestamp}.mp4"
    full_path = os.path.join(downloads_folder, filename)
    
    try:
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()
        
        with open(full_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return full_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio file to text using AWS Transcribe"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': f'Invalid audio file type. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'}), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Use AWS Transcribe or fallback
            if aws_enabled and aws_helper:
                result = aws_helper.transcribe_audio(temp_path)
            else:
                result = transcribe_audio_fallback(temp_path)
            
            return jsonify(result)
        
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    """Translate text using AWS Translate"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_language = data.get('target_language', 'es')
        
        if not text:
            return jsonify({'error': 'No text provided for translation'}), 400
        
        # Use AWS Translate or fallback
        if aws_enabled and aws_helper:
            result = aws_helper.translate_text(text, target_language)
        else:
            result = translate_text_fallback(text, target_language)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Generate content using AWS Bedrock"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        content_type = data.get('content_type', 'script')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided for content generation'}), 400
        
        # Use AWS Bedrock or fallback
        if aws_enabled and aws_helper:
            result = aws_helper.generate_content(prompt, content_type)
        else:
            result = generate_content_fallback(prompt, content_type)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Content generation failed: {str(e)}'}), 500

@app.route('/generate', methods=['POST'])
def generate_lipsync():
    try:
        print("=== DEBUG: Starting generate_lipsync ===")
        print(f"Request form keys: {list(request.form.keys())}")
        print(f"Request files keys: {list(request.files.keys())}")
        
        # Get form data
        api_key = request.form.get('api_key')
        audio_input_type = request.form.get('audio_input_type', 'text')
        
        print(f"API Key provided: {'Yes' if api_key else 'No'}")
        print(f"Audio input type: {audio_input_type}")
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        # Handle audio input (text-to-speech or uploaded audio)
        payload = {}
        input_audio_file = None
        
        if audio_input_type == 'text':
            text_prompt = request.form.get('text_prompt')
            print(f"Text prompt: {text_prompt}")
            if not text_prompt:
                return jsonify({'error': 'Text prompt is required when using text-to-speech'}), 400
            
            payload = {
                "text_prompt": text_prompt,
                "tts_provider": "OPEN_AI",
            }
            api_endpoint = "https://api.gooey.ai/v2/LipsyncTTS?example_id=eurnuoea63jk"
            
        elif audio_input_type == 'audio':
            # Handle audio file upload
            input_audio_file = None
            if 'input_audio' in request.files:
                file = request.files['input_audio']
                print(f"Audio file: {file.filename}")
                print(f"Content type: {file.content_type}")
                print(f"Content length: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")
                
                if file.filename != '':
                    # Validate file type
                    if not allowed_file(file.filename, 'audio'):
                        return jsonify({'error': f'Invalid audio file type. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'}), 400
                    
                    input_audio_file = file
            
            if not input_audio_file:
                return jsonify({'error': 'Audio file is required when using audio upload'}), 400
            
            # We'll handle this differently - use multipart form data
            api_endpoint = "https://api.gooey.ai/v2/Lipsync?example_id=ec0kkokbz61h"
        
        else:
            return jsonify({'error': 'Invalid audio input type'}), 400
        
        # Handle image upload (optional for some endpoints)
        input_face_file = None
        input_face_url = None
        
        if 'input_face' in request.files:
            file = request.files['input_face']
            print(f"Face file: {file.filename}")
            if file.filename != '':
                input_face_file = file
        
        # Use URL if provided instead of file upload
        if not input_face_file and request.form.get('input_face_url'):
            input_face_url = request.form.get('input_face_url')
            print(f"Face URL provided: {input_face_url}")
        
        # Check face requirement for TTS endpoint
        if audio_input_type == 'text' and not input_face_file and not input_face_url:
            return jsonify({'error': 'Face image is required when using text-to-speech'}), 400
        
        print(f"API endpoint: {api_endpoint}")
        
        # Make request to Gooey API
        print("Making request to Gooey API...")
        
        if audio_input_type == 'text':
            # For text-to-speech, use JSON payload
            if input_face_file:
                # Convert face image to base64 for TTS endpoint
                try:
                    input_face_data = upload_file_to_base64(input_face_file)
                    payload["input_face"] = input_face_data
                except Exception as e:
                    print(f"Error processing face image: {e}")
                    return jsonify({'error': f'Failed to process face image: {str(e)}'}), 400
            elif input_face_url:
                payload["input_face"] = input_face_url
            
            print(f"Final payload (TTS): {list(payload.keys())}")
            
            response = requests.post(
                api_endpoint,
                headers={
                    "Authorization": f"bearer {api_key}",
                },
                json=payload,
            )
        else:
            # For audio upload, use multipart form data
            files = {}
            data = {}
            
            # Add audio file - read the content properly
            input_audio_file.seek(0)  # Reset file pointer
            audio_content = input_audio_file.read()
            input_audio_file.seek(0)  # Reset again for potential reuse
            
            files['input_audio'] = (
                input_audio_file.filename, 
                audio_content,
                input_audio_file.content_type or 'audio/mpeg'
            )
            
            # Add face image/URL if provided
            if input_face_file:
                input_face_file.seek(0)  # Reset file pointer
                face_content = input_face_file.read()
                input_face_file.seek(0)  # Reset again
                
                files['input_face'] = (
                    input_face_file.filename, 
                    face_content,
                    input_face_file.content_type or 'image/jpeg'
                )
            elif input_face_url:
                data['input_face'] = input_face_url
            
            print(f"Form data keys: {list(data.keys())}")
            print(f"Files keys: {list(files.keys())}")
            print(f"Audio file size: {len(audio_content)} bytes")
            print(f"Audio file type: {input_audio_file.content_type}")
            print(f"Audio filename: {input_audio_file.filename}")
            
            # Validate audio content
            if len(audio_content) == 0:
                return jsonify({'error': 'Audio file is empty'}), 400
            
            if len(audio_content) > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({'error': 'Audio file too large (max 10MB)'}), 400
            
            response = requests.post(
                api_endpoint,
                headers={
                    "Authorization": f"bearer {api_key}",
                },
                files=files,
                data=data,
            )
        
        print(f"API Response status: {response.status_code}")
        print(f"API Response content: {response.text[:500]}...")
        
        if not response.ok:
            return jsonify({'error': f'API request failed: {response.status_code} - {response.text}'}), 400
        
        result = response.json()
        
        # Extract video URL
        if 'output' in result and 'output_video' in result['output']:
            video_url = result['output']['output_video']
            print(f"Video URL: {video_url}")
            
            # Download video to Downloads folder
            downloaded_path = download_video(video_url, api_key)
            
            if downloaded_path:
                return jsonify({
                    'success': True,
                    'video_url': video_url,
                    'downloaded_path': downloaded_path,
                    'message': f'Video successfully generated and saved to Downloads folder!'
                })
            else:
                return jsonify({
                    'success': True,
                    'video_url': video_url,
                    'message': 'Video generated successfully! You can download it from the provided URL.',
                    'warning': 'Failed to automatically download to Downloads folder'
                })
        else:
            print(f"No output_video found in result: {result}")
            return jsonify({'error': 'No video URL found in API response'}), 400
            
    except Exception as e:
        print(f"ERROR in generate_lipsync: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
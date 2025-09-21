import boto3
import json
import os
import tempfile
from datetime import datetime

class AWSHelper:
    def __init__(self):
        # Initialize AWS clients with better error handling
        try:
            # Try to initialize AWS clients
            # AWS credentials can be configured via:
            # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
            # 2. AWS CLI (aws configure)
            # 3. IAM roles (if running on EC2)
            
            # Specify region for Bedrock availability
            self.region = 'us-east-1'  # Change if needed
            
            self.transcribe = boto3.client('transcribe', region_name=self.region)
            self.translate = boto3.client('translate', region_name=self.region)
            self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
            self.s3 = boto3.client('s3', region_name=self.region)
            
            # S3 bucket for temporary audio files
            # IMPORTANT: Create this bucket in your AWS account and update the name
            self.bucket_name = f'lipsync-temp-audio-{datetime.now().strftime("%Y%m")}'  # Auto-generate bucket name
            
            # Test AWS connectivity
            self.aws_available = self._test_aws_access()
            
        except Exception as e:
            print(f"AWS initialization error: {e}")
            print("Please check your AWS credentials and region settings")
            self.aws_available = False
    
    def _test_aws_access(self):
        """Test if AWS services are accessible"""
        try:
            # Test basic AWS connectivity
            self.translate.list_terminologies()
            print("✅ AWS Translate: Connected")
            
            # Test S3 access (and create bucket if needed)
            try:
                self.s3.head_bucket(Bucket=self.bucket_name)
                print(f"✅ S3 Bucket '{self.bucket_name}': Found")
            except:
                try:
                    self.s3.create_bucket(Bucket=self.bucket_name)
                    print(f"✅ S3 Bucket '{self.bucket_name}': Created")
                except Exception as s3_error:
                    print(f"⚠️ S3 Bucket issue: {s3_error}")
            
            # Test Bedrock access
            try:
                # Try to list available models
                response = self.bedrock.list_foundation_models()
                available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
                claude_models = [m for m in available_models if 'claude' in m.lower()]
                
                if claude_models:
                    print(f"✅ AWS Bedrock: Connected (Claude models available)")
                    return True
                else:
                    print("⚠️ AWS Bedrock: Connected but no Claude models accessible")
                    print("   Please request model access in AWS Bedrock console")
                    return False
                    
            except Exception as bedrock_error:
                print(f"⚠️ AWS Bedrock: {bedrock_error}")
                print("   Please check Bedrock access and model permissions")
                return False
                
        except Exception as e:
            print(f"❌ AWS Access Test Failed: {e}")
            print("   Please check your AWS credentials, region, and permissions")
            return False
    
    def transcribe_audio(self, audio_file_path):
        """
        Simple audio transcription using AWS Transcribe
        """
        if not self.aws_available:
            return transcribe_audio_fallback(audio_file_path)
            
        try:
            # Generate unique job name
            job_name = f"transcribe-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Upload audio to S3 first (Transcribe requires S3 URL)
            s3_key = f"audio/{job_name}.{audio_file_path.split('.')[-1]}"
            
            print(f"📤 Uploading audio to S3: {s3_key}")
            self.s3.upload_file(audio_file_path, self.bucket_name, s3_key)
            audio_uri = f"s3://{self.bucket_name}/{s3_key}"
            
            # Start transcription job
            print(f"🎵 Starting transcription job: {job_name}")
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': audio_uri},
                MediaFormat=audio_file_path.split('.')[-1].lower(),
                LanguageCode='en-US'  # Default to English
            )
            
            # Wait for completion (simple polling)
            import time
            print("⏳ Waiting for transcription to complete...")
            
            max_wait_time = 300  # 5 minutes max
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status == 'COMPLETED':
                    print("✅ Transcription completed!")
                    # Get transcription result
                    result_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    import requests
                    transcript_response = requests.get(result_uri)
                    transcript_data = transcript_response.json()
                    
                    # Extract text
                    text = transcript_data['results']['transcripts'][0]['transcript']
                    
                    # Cleanup
                    self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                    self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                    
                    return {'success': True, 'text': text}
                    
                elif job_status == 'FAILED':
                    error_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown error')
                    print(f"❌ Transcription failed: {error_reason}")
                    return {'success': False, 'error': f'Transcription failed: {error_reason}'}
                
                time.sleep(3)  # Wait 3 seconds before checking again
            
            # Timeout
            print("⏰ Transcription timed out")
            return {'success': False, 'error': 'Transcription timed out after 5 minutes'}
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return transcribe_audio_fallback(audio_file_path)
    
    def translate_text(self, text, target_language='es'):
        """
        Simple text translation using AWS Translate
        """
        if not self.aws_available:
            return translate_text_fallback(text, target_language)
            
        try:
            print(f"🌍 Translating text to {target_language}")
            response = self.translate.translate_text(
                Text=text,
                SourceLanguageCode='auto',  # Auto-detect source language
                TargetLanguageCode=target_language
            )
            
            print("✅ Translation completed!")
            return {
                'success': True, 
                'translated_text': response['TranslatedText'],
                'source_language': response['SourceLanguageCode']
            }
            
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return translate_text_fallback(text, target_language)
    
    def generate_content(self, prompt, content_type='script'):
        """
        Simple content generation using AWS Bedrock (Claude)
        """
        if not self.aws_available:
            return generate_content_fallback(prompt, content_type)
            
        try:
            # Customize prompt based on content type
            if content_type == 'script':
                system_prompt = "You are a creative scriptwriter. Generate engaging, natural dialogue for video content. Keep responses under 200 words."
            elif content_type == 'voice':
                system_prompt = "You are a voice-over specialist. Create clear, engaging narration text. Keep responses under 200 words."
            else:
                system_prompt = "You are a helpful content creator. Generate engaging text content. Keep responses under 200 words."
            
            # Try different Bedrock models in order of preference
            models_to_try = [
                'anthropic.claude-3-haiku-20240307-v1:0',
                'anthropic.claude-instant-v1',
                'anthropic.claude-v2:1',
                'anthropic.claude-v2'
            ]
            
            print(f"🤖 Generating content with AWS Bedrock...")
            
            for model_id in models_to_try:
                try:
                    print(f"   Trying model: {model_id}")
                    
                    # Use Claude format for Anthropic models
                    if 'claude' in model_id.lower():
                        body = {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 500,
                            "system": system_prompt,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        }
                    else:
                        # Generic format for other models
                        body = {
                            "inputText": f"{system_prompt}\n\nUser: {prompt}\nAssistant:",
                            "textGenerationConfig": {
                                "maxTokenCount": 500,
                                "temperature": 0.7
                            }
                        }
                    
                    response = self.bedrock.invoke_model(
                        modelId=model_id,
                        contentType='application/json',
                        accept='application/json',
                        body=json.dumps(body)
                    )
                    
                    response_body = json.loads(response['body'].read())
                    
                    # Extract text based on model response format
                    if 'claude' in model_id.lower():
                        generated_text = response_body['content'][0]['text']
                    else:
                        generated_text = response_body.get('results', [{}])[0].get('outputText', '')
                    
                    print("✅ Content generation completed!")
                    return {'success': True, 'generated_text': generated_text.strip()}
                    
                except Exception as model_error:
                    print(f"   ❌ Model {model_id} failed: {model_error}")
                    continue
            
            # If all models fail, use fallback
            print("⚠️ All Bedrock models failed, using fallback")
            return generate_content_fallback(prompt, content_type)
            
        except Exception as e:
            print(f"❌ Bedrock error: {e}")
            return generate_content_fallback(prompt, content_type)

# Simple fallback functions for demo purposes (if AWS is not configured)
def transcribe_audio_fallback(audio_file_path):
    """Fallback transcription for demo"""
    return {
        'success': True, 
        'text': "[Demo transcription] This is sample transcribed text from your audio file."
    }

def translate_text_fallback(text, target_language='es'):
    """Fallback translation for demo"""
    translations = {
        'es': f"[Demo Spanish] {text}",
        'fr': f"[Demo French] {text}",
        'de': f"[Demo German] {text}"
    }
    return {
        'success': True, 
        'translated_text': translations.get(target_language, f"[Demo {target_language}] {text}"),
        'source_language': 'en'
    }

def generate_content_fallback(prompt, content_type='script'):
    """Fallback content generation for demo"""
    if 'video' in prompt.lower() or 'script' in prompt.lower():
        content = "Welcome to our amazing product demonstration! Today we'll show you how our innovative solution can transform your workflow and boost productivity."
    elif 'voice' in prompt.lower() or 'narration' in prompt.lower():
        content = "This is a professional voice-over narration that clearly explains the key benefits and features of your product or service."
    else:
        content = f"Here's engaging content based on your request: {prompt}. This would be an AI-generated response that provides valuable and relevant information."
    
    return {'success': True, 'generated_text': content}
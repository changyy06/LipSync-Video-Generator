import boto3
import json
import os
import tempfile
import time
import requests
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from aws_config import AWS_REGIONS, get_bedrock_models, get_models_for_region

# Google Translate integration
try:
    from googletrans import Translator
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False
    print("⚠️ Google Translate not available. Install with: pip install googletrans==4.0.0rc1")

# Import our region configuration
try:
    from aws_config import get_region_for_service, get_alternative_regions, get_models_for_region
except ImportError:
    # Fallback if config file doesn't exist
    def get_region_for_service(service):
        regions = {
            'default': 'ap-southeast-1',
            'transcribe': 'ap-southeast-1', 
            'translate': 'us-east-1',
            'bedrock': 'us-east-1'
        }
        return regions.get(service, 'ap-southeast-1')
    
    def get_alternative_regions(service):
        return ['us-east-1', 'us-west-2']
    
    def get_models_for_region(region):
        return {}

class AWSHelper:
    def __init__(self):
        """Initialize AWS clients with region-specific configuration"""
        self.aws_available = False
        self.transcribe_available = False
        self.translate_available = False  # AWS Translate
        self.google_translate_available = GOOGLE_TRANSLATE_AVAILABLE
        self.bedrock_available = False
        
        # Use different regions for different services
        self.transcribe_region = AWS_REGIONS.get('transcribe', 'ap-southeast-1')
        self.translate_region = AWS_REGIONS.get('translate', 'us-east-1')
        self.bedrock_region = AWS_REGIONS.get('bedrock', 'us-east-1')
        self.s3_region = AWS_REGIONS.get('default', 'ap-southeast-1')
        
        try:
            # Initialize clients with their respective regions
            self.transcribe = boto3.client('transcribe', region_name=self.transcribe_region)
            self.translate = boto3.client('translate', region_name=self.translate_region)
            self.bedrock = boto3.client('bedrock-runtime', region_name=self.bedrock_region)
            self.s3 = boto3.client('s3', region_name=self.s3_region)
            
            # Create unique bucket name
            self.bucket_name = 'lipsync-temp-audio-chang-2025'  # Using the bucket we just created
            
            # Initialize Google Translate
            if self.google_translate_available:
                self.google_translator = Translator()
                print("✅ Google Translate: Ready")
            else:
                print("❌ Google Translate: Not available")
            
            print(f"🌍 AWS Regions configured:")
            print(f"   Transcribe: {self.transcribe_region}")
            print(f"   Translate: {self.translate_region} (AWS blocked - using Google)")
            print(f"   Bedrock: {self.bedrock_region}")
            print(f"   S3: {self.s3_region}")
            
            # Test and setup
            self._setup_aws_services()
            
        except NoCredentialsError:
            print("❌ No AWS credentials found!")
            print("   Please run: python setup_aws.py")
        except Exception as e:
            print(f"❌ AWS setup failed: {e}")
        self.transcribe_available = False
        self.translate_available = False
        self.bedrock_available = False
        
        # Define regions for each service (you can customize in aws_config.py)
        self.default_region = os.environ.get('AWS_DEFAULT_REGION') or get_region_for_service('default')
        self.transcribe_region = os.environ.get('AWS_TRANSCRIBE_REGION') or get_region_for_service('transcribe')
        self.translate_region = os.environ.get('AWS_TRANSLATE_REGION') or get_region_for_service('translate')
        self.bedrock_region = os.environ.get('AWS_BEDROCK_REGION') or get_region_for_service('bedrock')
        self.s3_region = self.default_region  # S3 bucket region
        
        try:
            # Initialize clients with service-specific regions
            self.transcribe = boto3.client('transcribe', region_name=self.transcribe_region)
            self.translate = boto3.client('translate', region_name=self.translate_region)
            self.bedrock = boto3.client('bedrock-runtime', region_name=self.bedrock_region)
            self.s3 = boto3.client('s3', region_name=self.s3_region)
            
            # Create unique bucket name
            self.bucket_name = 'lipsync-temp-audio-chang-2025'  # Using the bucket we just created
            
            print(f"🌍 Service regions:")
            print(f"   Transcribe: {self.transcribe_region}")
            print(f"   Translate: {self.translate_region}")
            print(f"   Bedrock: {self.bedrock_region}")
            print(f"   S3: {self.s3_region}")
            
            # Test and setup
            self._setup_aws_services()
            
        except NoCredentialsError:
            print("❌ No AWS credentials found!")
            print("   Please run: python setup_aws.py")
        except Exception as e:
            print(f"❌ AWS setup failed: {e}")
    
    def _setup_aws_services(self):
        """Setup required AWS services with individual testing"""
        try:
            # Test basic connectivity
            sts = boto3.client('sts', region_name=self.default_region)
            identity = sts.get_caller_identity()
            print(f"✅ AWS Connected as: {identity.get('Arn', 'Unknown')}")
            
            # Setup S3 bucket
            self._setup_s3_bucket()
            
            # Test each service individually
            self._test_transcribe()
            self._test_translate()
            self._test_bedrock()
            
            # Set overall availability if at least one service works
            self.aws_available = any([self.transcribe_available, self.google_translate_available, self.bedrock_available])
            
            # Report status
            working_services = []
            if self.transcribe_available:
                working_services.append(f"Transcribe ({self.transcribe_region})")
            if self.google_translate_available:
                working_services.append("Google Translate")
            if self.bedrock_available:
                working_services.append(f"Bedrock ({self.bedrock_region})")
                
            if working_services:
                print(f"🚀 Working services: {', '.join(working_services)}")
            else:
                print("⚠️ No services available")
            
        except Exception as e:
            print(f"⚠️ AWS service test failed: {e}")
            self.aws_available = False
    
    def _test_transcribe(self):
        """Test Transcribe service"""
        try:
            self.transcribe.list_transcription_jobs(MaxResults=1)
            self.transcribe_available = True
            print(f"✅ AWS Transcribe ({self.transcribe_region}): Ready")
        except Exception as e:
            print(f"❌ AWS Transcribe ({self.transcribe_region}) blocked: {str(e)[:60]}...")
            self.transcribe_available = False
    
    def _test_translate(self):
        """Test Translate service with fallback regions"""
        primary_region = self.translate_region
        
        # Try primary region first
        try:
            self.translate.translate_text(
                Text="Hello",
                SourceLanguageCode='en',
                TargetLanguageCode='es'
            )
            self.translate_available = True
            print(f"✅ AWS Translate ({primary_region}): Ready")
            return
        except Exception as e:
            print(f"❌ AWS Translate ({primary_region}) failed: {str(e)[:60]}...")
        
        # Try alternative regions
        alt_regions = get_alternative_regions('translate')
        for region in alt_regions:
            if region == primary_region:
                continue  # Skip the region we already tried
                
            try:
                print(f"🔄 Trying Translate in {region}...")
                alt_client = boto3.client('translate', region_name=region)
                alt_client.translate_text(
                    Text="Hello",
                    SourceLanguageCode='en',
                    TargetLanguageCode='es'
                )
                # Success! Update our client and region
                self.translate = alt_client
                self.translate_region = region
                self.translate_available = True
                print(f"✅ AWS Translate ({region}): Ready (fallback)")
                return
            except Exception as e:
                print(f"❌ AWS Translate ({region}) also failed: {str(e)[:40]}...")
        
        # All regions failed
        self.translate_available = False
        print("❌ AWS Translate: No working regions found")
    
    def _test_bedrock(self):
        """Test Bedrock service with DeepSeek priority in us-east-1"""
        primary_region = self.bedrock_region
        models_to_try = get_bedrock_models()
        
        print(f"🤖 Testing Bedrock in {primary_region} (DeepSeek On-Demand priority)...")
        
        # Prioritize DeepSeek models for us-east-1
        deepseek_models = [m for m in models_to_try if 'deepseek' in m.lower()]
        other_models = [m for m in models_to_try if 'deepseek' not in m.lower()]
        
        # Test DeepSeek models first if we're in us-east-1
        if primary_region == 'us-east-1':
            test_order = deepseek_models + other_models[:5]  # DeepSeek + top 5 others
            print(f"   🎯 Prioritizing DeepSeek models for {primary_region}")
        else:
            test_order = models_to_try[:8]  # Standard test order
            
        # Try primary region first
        for model_id in test_order:
            try:
                # Check if this is an inference profile ARN
                is_inference_profile = model_id.startswith('arn:aws:bedrock:') and 'inference-profile' in model_id
                
                if is_inference_profile:
                    # Use converse API for inference profiles (like DeepSeek R1)
                    body = {
                        "messages": [{"role": "user", "content": [{"text": "Hello"}]}],
                        "inferenceConfig": {
                            "maxTokens": 20,
                            "temperature": 1.0,
                            "topP": 0.9
                        }
                    }
                    
                    response = self.bedrock.converse(
                        modelId=model_id,
                        messages=body["messages"],
                        inferenceConfig=body["inferenceConfig"]
                    )
                    
                    # Just check if we get a valid response structure
                    if 'output' in response and 'message' in response['output']:
                        # Success - model is accessible
                        pass
                    else:
                        raise Exception("Invalid response structure")
                    
                elif 'deepseek' in model_id:
                    # Standard DeepSeek models format
                    body = {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 20,
                        "temperature": 0.1
                    }
                    
                    response = self.bedrock.invoke_model(
                        modelId=model_id,
                        contentType='application/json',
                        accept='application/json',
                        body=json.dumps(body)
                    )
                    
                elif 'nova' in model_id:
                    body = {
                        "inputText": "Hello",
                        "textGenerationConfig": {
                            "maxTokenCount": 20,
                            "temperature": 0.1
                        }
                    }
                    
                    response = self.bedrock.invoke_model(
                        modelId=model_id,
                        contentType='application/json',
                        accept='application/json',
                        body=json.dumps(body)
                    )
                    
                elif 'llama' in model_id:
                    body = {
                        "prompt": "Hello",
                        "max_gen_len": 20,
                        "temperature": 0.1
                    }
                    
                    response = self.bedrock.invoke_model(
                        modelId=model_id,
                        contentType='application/json',
                        accept='application/json',
                        body=json.dumps(body)
                    )
                    
                else:
                    # Claude models format
                    body = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 20,
                        "messages": [{"role": "user", "content": "Hello"}]
                    }
                    
                    response = self.bedrock.invoke_model(
                        modelId=model_id,
                        contentType='application/json',
                        accept='application/json',
                        body=json.dumps(body)
                    )
                
                self.bedrock_available = True
                print(f"✅ AWS Bedrock ({primary_region}): Ready with {model_id}")
                if 'deepseek' in model_id:
                    print(f"   🎉 DeepSeek model working! Perfect for coding tasks.")
                return
                
            except Exception as model_error:
                if "does not have access" in str(model_error) or "access denied" in str(model_error).lower():
                    if 'deepseek' in model_id:
                        print(f"🔐 DeepSeek {model_id} needs access approval in {primary_region}")
                    else:
                        print(f"🔐 Model {model_id} needs access approval")
                else:
                    print(f"⚠️ Model {model_id} failed: {str(model_error)[:60]}...")
                continue
        
        print(f"❌ No models accessible in {primary_region}")
        
        # Try alternative regions if primary fails
        alt_regions = get_alternative_regions('bedrock')
        for region in alt_regions:
            if region == primary_region:
                continue  # Skip the region we already tried
                
            try:
                print(f"🔄 Trying Bedrock in {region}...")
                alt_client = boto3.client('bedrock-runtime', region_name=region)
                
                # Try basic Claude model in alternative region (most widely available)
                test_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 20,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
                
                alt_client.invoke_model(
                    modelId='anthropic.claude-3-haiku-20240307-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(test_body)
                )
                
                # Success! Update our client and region
                self.bedrock = alt_client
                self.bedrock_region = region
                self.bedrock_available = True
                print(f"✅ AWS Bedrock ({region}): Ready (fallback)")
                return
            except Exception as e:
                print(f"❌ AWS Bedrock ({region}) also failed: {str(e)[:40]}...")
        
        # All regions failed
        self.bedrock_available = False
        print("❌ AWS Bedrock: No working regions found")
        print("   💡 Try requesting DeepSeek model access in AWS Console > Bedrock > Model Access")
        print("   🎯 Focus on: DeepSeek V2.5 Chat & DeepSeek Coder V2 Instruct for us-east-1")
    
    def _setup_s3_bucket(self):
        """Check S3 bucket access"""
        try:
            # Check if bucket exists and is accessible
            self.s3.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket ready: {self.bucket_name}")
        except ClientError as e:
            print(f"❌ S3 bucket access failed: {e}")
            raise
    
    def _test_bedrock_access(self):
        """Legacy method - kept for compatibility"""
        return self._test_bedrock()
    
    def transcribe_audio(self, audio_file_path):
        """Real AWS Transcribe implementation"""
        if not self.transcribe_available:
            return {'success': False, 'error': 'AWS Transcribe not available due to permissions'}
        
        try:
            # Generate unique job name
            job_name = f"transcribe-{int(time.time())}"
            file_ext = audio_file_path.split('.')[-1].lower()
            s3_key = f"audio/{job_name}.{file_ext}"
            
            print(f"📤 Uploading {os.path.basename(audio_file_path)} to S3...")
            
            # Upload to S3
            self.s3.upload_file(audio_file_path, self.bucket_name, s3_key)
            audio_uri = f"s3://{self.bucket_name}/{s3_key}"
            
            print(f"🎵 Starting transcription job...")
            
            # Start transcription
            response = self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': audio_uri},
                MediaFormat=file_ext if file_ext in ['mp3', 'mp4', 'wav', 'flac'] else 'mp3',
                LanguageCode='en-US'
            )
            
            # Wait for completion
            print("⏳ Waiting for transcription...")
            max_wait = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = self.transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                status = status_response['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    # Get result
                    transcript_uri = status_response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    
                    # Download transcript
                    transcript_response = requests.get(transcript_uri)
                    transcript_data = transcript_response.json()
                    
                    text = transcript_data['results']['transcripts'][0]['transcript']
                    
                    # Cleanup
                    self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                    self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                    
                    print(f"✅ Transcription completed: {len(text)} characters")
                    return {'success': True, 'text': text}
                    
                elif status == 'FAILED':
                    failure_reason = status_response['TranscriptionJob'].get('FailureReason', 'Unknown')
                    print(f"❌ Transcription failed: {failure_reason}")
                    return {'success': False, 'error': f'Transcription failed: {failure_reason}'}
                
                time.sleep(5)
            
            print("⏰ Transcription timed out")
            return {'success': False, 'error': 'Transcription timed out'}
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return {'success': False, 'error': str(e)}
    
    def translate_text(self, text, target_language='es'):
        """Google Translate implementation (AWS Translate is blocked)"""
        if not self.google_translate_available:
            # Simple fallback if Google Translate isn't available
            fallback_translations = {
                'es': f"[Traducción no disponible] Original: {text}",
                'fr': f"[Traduction non disponible] Original: {text}",
                'de': f"[Übersetzung nicht verfügbar] Original: {text}",
                'it': f"[Traduzione non disponibile] Original: {text}",
                'ja': f"[翻訳は利用できません] Original: {text}",
                'pt': f"[Tradução não disponível] Original: {text}",
                'zh': f"[翻译不可用] Original: {text}"
            }
            
            translated = fallback_translations.get(target_language, f"[Translation to {target_language} not available] Original: {text}")
            
            return {
                'success': True,
                'translated_text': translated,
                'source_language': 'en',
                'note': 'Translation service not available - using fallback'
            }
        
        try:
            print(f"🌍 Translating to {target_language} with Google Translate...")
            
            # Use Google Translate
            result = self.google_translator.translate(
                text, 
                src='auto',  # Auto-detect source language
                dest=target_language
            )
            
            print(f"✅ Translation completed ({result.src} → {target_language})")
            return {
                'success': True,
                'translated_text': result.text,
                'source_language': result.src,
                'confidence': getattr(result, 'confidence', None),
                'service': 'Google Translate'
            }
            
        except Exception as e:
            print(f"❌ Google Translate error: {e}")
            
            # Fallback to simple substitution
            fallback_translations = {
                'es': f"[Error en traducción] Texto original: {text}",
                'fr': f"[Erreur de traduction] Texte original: {text}",
                'de': f"[Übersetzungsfehler] Originaltext: {text}",
                'it': f"[Errore di traduzione] Testo originale: {text}",
                'ja': f"[翻訳エラー] 元のテキスト: {text}",
                'pt': f"[Erro de tradução] Texto original: {text}",
                'zh': f"[翻译错误] 原文: {text}"
            }
            
            fallback_text = fallback_translations.get(target_language, f"[Translation error to {target_language}] Original: {text}")
            
            return {
                'success': True,
                'translated_text': fallback_text,
                'source_language': 'en',
                'error': str(e),
                'service': 'Fallback'
            }
    
    def generate_content(self, prompt, content_type='script'):
        """Real AWS Bedrock implementation with fallback"""
        if not self.bedrock_available:
            # Provide a simple fallback for content generation
            fallback_content = {
                'script': f"[AWS Bedrock blocked by policy]\n\nGenerated Script for: {prompt}\n\nThis is a placeholder script. Your actual content would be:\n• Engaging opening\n• Key message delivery\n• Strong conclusion\n\nPlease configure AWS Bedrock access to generate real AI content.",
                'voice': f"[AWS Bedrock blocked by policy]\n\nVoice-over for: {prompt}\n\nThis is a placeholder narration. Your professional voice-over would include:\n• Clear pronunciation guide\n• Natural pacing cues\n• Engaging delivery style\n\nPlease configure AWS Bedrock access for AI-generated narration.",
                'general': f"[AWS Bedrock blocked by policy]\n\nContent for: {prompt}\n\nThis is placeholder content. Your AI-generated content would be:\n• Professionally written\n• Tailored to your needs\n• Ready to use\n\nPlease configure AWS Bedrock access for real AI content generation."
            }
            
            generated_text = fallback_content.get(content_type, fallback_content['general'])
            
            return {
                'success': True, 
                'generated_text': generated_text,
                'note': 'AWS Bedrock blocked by service control policy - using fallback'
            }
        
        try:
            print(f"🤖 Generating {content_type} content...")
            
            # Customize system prompt
            system_prompts = {
                'script': "You are a professional scriptwriter. Create engaging video scripts that are clear, compelling, and under 200 words.",
                'voice': "You are a voice-over specialist. Create professional narration that's easy to speak and engaging to listen to, under 200 words.",
                'general': "You are a content creator. Generate engaging, informative content under 200 words."
            }
            
            system_prompt = system_prompts.get(content_type, system_prompts['general'])
            
            # Try different models
            models = get_bedrock_models()
            
            for model_id in models:
                try:
                    # Check if this is an inference profile ARN  
                    is_inference_profile = model_id.startswith('arn:aws:bedrock:') and 'inference-profile' in model_id
                    
                    if is_inference_profile:
                        # Use converse API for inference profiles (like DeepSeek R1)
                        # DeepSeek R1 needs more tokens as it shows reasoning process
                        response = self.bedrock.converse(
                            modelId=model_id,
                            messages=[
                                {"role": "user", "content": [{"text": f"Please provide a direct, concise answer without showing your reasoning process.\n\n{system_prompt}\n\nUser request: {prompt}\n\nProvide only the final content:"}]}
                            ],
                            inferenceConfig={
                                "maxTokens": 1000,  # Increased for reasoning models
                                "temperature": 0.7,
                                "topP": 0.9
                            }
                        )
                        
                        # Extract text from converse response - handle DeepSeek R1 structure
                        try:
                            content_array = response['output']['message']['content']
                            generated_text = ""
                            
                            # Look through all content items for the final answer
                            for content_item in content_array:
                                if 'text' in content_item:
                                    # Direct text content (final answer)
                                    generated_text = content_item['text']
                                    break
                                elif 'reasoningContent' in content_item:
                                    # Reasoning content - look for the final answer at the end
                                    reasoning_text = content_item['reasoningContent']['reasoningText']['text']
                                    
                                    # Try to extract final answer from reasoning
                                    # Look for patterns like "Final answer:", "Result:", etc.
                                    lines = reasoning_text.split('\n')
                                    for line in reversed(lines):  # Start from the end
                                        line = line.strip()
                                        if line and not line.startswith(('Let me', 'I need', 'The user', 'Wait', 'Hmm', 'Maybe', 'So')):
                                            # This might be the final answer
                                            generated_text = line
                                            break
                                    
                                    # If no clear final answer found, use the last part of reasoning
                                    if not generated_text and len(reasoning_text) > 100:
                                        generated_text = reasoning_text[-200:].split('\n')[-1].strip()
                                    elif not generated_text:
                                        generated_text = reasoning_text
                            
                            # Fallback if still no text
                            if not generated_text:
                                generated_text = f"[DeepSeek R1 response for: {prompt[:50]}...]"
                                
                        except (KeyError, IndexError) as e:
                            print(f"⚠️ Response parsing error for {model_id}: {e}")
                            continue
                        
                    elif 'nova' in model_id:
                        # Nova models use a different format
                        body = {
                            "inputText": f"{system_prompt}\n\nUser: {prompt}",
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
                        generated_text = response_body.get('outputText', '')
                        
                    elif 'llama' in model_id:
                        # Llama models format
                        body = {
                            "prompt": f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:",
                            "max_gen_len": 500,
                            "temperature": 0.7
                        }
                        
                        response = self.bedrock.invoke_model(
                            modelId=model_id,
                            contentType='application/json',
                            accept='application/json',
                            body=json.dumps(body)
                        )
                        
                        response_body = json.loads(response['body'].read())
                        generated_text = response_body.get('generation', '')
                        
                    elif 'deepseek' in model_id:
                        # DeepSeek models format
                        body = {
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "max_tokens": 500,
                            "temperature": 0.7
                        }
                        
                        response = self.bedrock.invoke_model(
                            modelId=model_id,
                            contentType='application/json',
                            accept='application/json',
                            body=json.dumps(body)
                        )
                        
                        response_body = json.loads(response['body'].read())
                        generated_text = response_body['choices'][0]['message']['content']
                        
                    else:
                        # Claude models format
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
                        
                        response = self.bedrock.invoke_model(
                            modelId=model_id,
                            contentType='application/json',
                            accept='application/json',
                            body=json.dumps(body)
                        )
                        
                        response_body = json.loads(response['body'].read())
                        generated_text = response_body['content'][0]['text']
                    
                    print(f"✅ Content generated with {model_id}")
                    return {'success': True, 'generated_text': generated_text.strip(), 'model_used': model_id}
                    
                except Exception as model_error:
                    if "does not have access" in str(model_error) or "access denied" in str(model_error).lower():
                        print(f"🔐 Model {model_id} needs access approval")
                    else:
                        print(f"⚠️ Model {model_id} failed: {str(model_error)[:60]}...")
                    continue
            
            return {'success': False, 'error': 'All Bedrock models failed'}
            
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            return {'success': False, 'error': str(e)}

# Fallback functions (only used if AWS is completely unavailable)
def transcribe_audio_fallback(audio_file_path):
    return {'success': False, 'error': 'AWS Transcribe not available. Please configure AWS credentials.'}

def translate_text_fallback(text, target_language='es'):
    return {'success': False, 'error': 'AWS Translate not available. Please configure AWS credentials.'}

def generate_content_fallback(prompt, content_type='script'):
    return {'success': False, 'error': 'AWS Bedrock not available. Please configure AWS credentials.'}
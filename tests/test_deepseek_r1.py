import boto3
import json
from botocore.exceptions import ClientError


def test_deepseek_r1_response_format():
    """Test DeepSeek R1 inference profile response format"""
    try:
        # Use default AWS configuration (from AWS CLI or environment)
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test the specific DeepSeek R1 inference profile
        deepseek_r1_arn = "arn:aws:bedrock:us-east-1:188473669770:inference-profile/us.deepseek.r1-v1:0"
        
        print(f"🧪 Testing DeepSeek R1 response format...")
        print(f"   Model: {deepseek_r1_arn}")
        
        try:
            response = client.converse(
                modelId=deepseek_r1_arn,
                messages=[
                    {"role": "user", "content": [{"text": "Say exactly: Hello from DeepSeek R1"}]}
                ],
                inferenceConfig={
                    "maxTokens": 50,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            )
            
            print(f"✅ DeepSeek R1 model accessible!")
            print(f"📋 Full Response Structure:")
            print(json.dumps(response, indent=2, default=str))
            
            # Extract response text
            try:
                generated_text = response['output']['message']['content'][0]['text']
                print(f"\n📝 Generated Text: {generated_text}")
                return True, generated_text
            except KeyError as e:
                print(f"❌ Response parsing error: {e}")
                print(f"   Response keys: {list(response.keys())}")
                if 'output' in response:
                    print(f"   Output keys: {list(response['output'].keys())}")
                return False, None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if 'AccessDenied' in error_code or 'does not have access' in str(e):
                print(f"🔐 DeepSeek R1 model needs access approval in us-east-1")
                print(f"   Go to AWS Console > Bedrock > Model access to request access")
            elif 'ThrottlingException' in error_code:
                print(f"⏱️ DeepSeek R1 model throttled - try again in a moment")
            else:
                print(f"❌ DeepSeek R1 test failed: {error_code}")
                print(f"   Error details: {e}")
            return False, None
            
    except Exception as e:
        print(f"❌ DeepSeek R1 test error: {e}")
        return False, None


def test_other_models():
    """Test other available models for comparison"""
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Try a few other models to see what works
    test_models = [
        "deepseek.deepseek-v2-5-chat-v1:0",
        "amazon.nova-micro-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0"
    ]
    
    print(f"\n🔍 Testing other models for comparison:")
    for model_id in test_models:
        try:
            if 'deepseek' in model_id:
                # Standard DeepSeek format
                body = {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 20,
                    "temperature": 0.1
                }
                
                response = client.invoke_model(
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                print(f"✅ {model_id}: Working")
                
            elif 'nova' in model_id:
                # Nova format
                body = {
                    "inputText": "Hello",
                    "textGenerationConfig": {
                        "maxTokenCount": 20,
                        "temperature": 0.1
                    }
                }
                
                response = client.invoke_model(
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                print(f"✅ {model_id}: Working")
                
            else:
                # Claude format
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 20,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
                
                response = client.invoke_model(
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                print(f"✅ {model_id}: Working")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if 'AccessDenied' in error_code:
                print(f"🔐 {model_id}: Access needed")
            elif 'ValidationException' in error_code:
                print(f"⚠️ {model_id}: Validation error (might need access)")
            else:
                print(f"❌ {model_id}: {error_code}")
        except Exception as e:
            print(f"❌ {model_id}: {str(e)[:50]}...")


if __name__ == "__main__":
    print("🧪 DeepSeek R1 Model Testing")
    print("=" * 50)
    
    # Test DeepSeek R1 specifically
    success, text = test_deepseek_r1_response_format()
    
    if success:
        print(f"\n🎉 DeepSeek R1 is working perfectly!")
        print(f"   Generated: '{text}'")
    else:
        print(f"\n❌ DeepSeek R1 needs troubleshooting")
    
    # Test other models for comparison
    test_other_models()
    
    print("\n✨ Testing complete!")
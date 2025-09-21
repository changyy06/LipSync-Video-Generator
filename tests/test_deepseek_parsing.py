import boto3
import json


def test_fixed_deepseek_r1():
    """Test the fixed DeepSeek R1 response parsing"""
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        deepseek_r1_arn = "arn:aws:bedrock:us-east-1:188473669770:inference-profile/us.deepseek.r1-v1:0"
        
        print(f"🧪 Testing fixed DeepSeek R1 response parsing...")
        
        response = client.converse(
            modelId=deepseek_r1_arn,
            messages=[
                {"role": "user", "content": [{"text": "Write a short script about AI being helpful. Keep it under 100 words."}]}
            ],
            inferenceConfig={
                "maxTokens": 200,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        print(f"✅ DeepSeek R1 response received!")
        
        # Apply the same parsing logic as our updated code
        try:
            content = response['output']['message']['content'][0]
            if 'text' in content:
                generated_text = content['text']
                print(f"📝 Found direct text content")
            elif 'reasoningContent' in content:
                # DeepSeek R1 has reasoning content
                generated_text = content['reasoningContent']['reasoningText']['text']
                print(f"🧠 Found reasoning content")
            else:
                # Fallback - look for any text content
                generated_text = str(content)
                print(f"⚠️ Using fallback content parsing")
                
            print(f"\n🎉 Generated Content:")
            print(f"{generated_text}")
            print(f"\n📊 Token Usage: {response['usage']['totalTokens']} tokens")
            return True, generated_text
            
        except (KeyError, IndexError) as e:
            print(f"❌ Parsing error: {e}")
            print(f"📋 Content structure: {json.dumps(response['output']['message']['content'], indent=2)}")
            return False, None
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, None


if __name__ == "__main__":
    print("🔧 Testing Fixed DeepSeek R1 Response Parsing")
    print("=" * 50)
    
    success, text = test_fixed_deepseek_r1()
    
    if success:
        print(f"\n✅ DeepSeek R1 parsing is now working correctly!")
        print(f"   Length: {len(text)} characters")
    else:
        print(f"\n❌ Still needs fixing")
    
    print("\n✨ Test complete!")
import boto3
import json


def test_improved_deepseek_parsing():
    """Test the improved DeepSeek R1 parsing with better prompting"""
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        deepseek_r1_arn = "arn:aws:bedrock:us-east-1:188473669770:inference-profile/us.deepseek.r1-v1:0"
        
        print("🔧 Testing Improved DeepSeek R1 Parsing")
        print("=" * 50)
        
        # Test with a direct prompt that requests no reasoning
        response = client.converse(
            modelId=deepseek_r1_arn,
            messages=[
                {"role": "user", "content": [{"text": "Please provide a direct, concise answer without showing your reasoning process.\n\nYou are a professional scriptwriter. Create engaging video scripts that are clear, compelling, and under 200 words.\n\nUser request: Write a 50-word script about the benefits of renewable energy\n\nProvide only the final content:"}]}
            ],
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        print("✅ Response received!")
        
        # Apply the improved parsing logic
        content_array = response['output']['message']['content']
        generated_text = ""
        
        print(f"📄 Content items: {len(content_array)}")
        
        # Look through all content items for the final answer
        for i, content_item in enumerate(content_array):
            print(f"\n  📄 Item {i} keys: {list(content_item.keys())}")
            
            if 'text' in content_item:
                # Direct text content (final answer)
                generated_text = content_item['text']
                print(f"  ✅ Found direct text: '{generated_text[:100]}...'")
                break
            elif 'reasoningContent' in content_item:
                # Reasoning content - look for the final answer at the end
                reasoning_text = content_item['reasoningContent']['reasoningText']['text']
                print(f"  🧠 Found reasoning content ({len(reasoning_text)} chars)")
                
                # Try to extract final answer from reasoning
                lines = reasoning_text.split('\n')
                for line in reversed(lines):  # Start from the end
                    line = line.strip()
                    if line and not line.startswith(('Let me', 'I need', 'The user', 'Wait', 'Hmm', 'Maybe', 'So', 'Okay')):
                        # This might be the final answer
                        generated_text = line
                        print(f"  🎯 Extracted final answer: '{generated_text[:100]}...'")
                        break
                
                # If no clear final answer found, use the last part of reasoning
                if not generated_text and len(reasoning_text) > 100:
                    generated_text = reasoning_text[-200:].split('\n')[-1].strip()
                    print(f"  📝 Using last reasoning line: '{generated_text[:100]}...'")
                elif not generated_text:
                    generated_text = reasoning_text
                    print(f"  📋 Using full reasoning text")
        
        # Final result
        if generated_text:
            print(f"\n🎉 Final Generated Text:")
            print(f"'{generated_text}'")
            print(f"\nLength: {len(generated_text)} characters")
            return True, generated_text
        else:
            print(f"\n❌ No text extracted")
            return False, None
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, None


if __name__ == "__main__":
    success, text = test_improved_deepseek_parsing()
    
    if success:
        print(f"\n✅ Improved parsing is working!")
    else:
        print(f"\n❌ Still needs work")
    
    print("\n✨ Test complete!")
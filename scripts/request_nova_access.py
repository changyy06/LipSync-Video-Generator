#!/usr/bin/env python3
"""
AWS Bedrock Model Access Helper

This script helps you:
1. Check current Bedrock model access
2. Provide instructions for requesting Nova, Llama, and DeepSeek model access
3. Test different regions for Bedrock availability
"""

import boto3
import json
from botocore.exceptions import ClientError
from aws_config import AWS_REGIONS, get_bedrock_models, get_models_for_region

def test_model_access(region='us-east-1'):
    """Test access to different Bedrock models"""
    print(f"\n🧪 Testing model access in {region}...")
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name=region)
        models_to_test = get_bedrock_models()
        
        accessible_models = []
        blocked_models = []
        
        for model_id in models_to_test:
            try:
                # Different body format for different models
                if 'nova' in model_id:
                    body = {
                        "inputText": "Test",
                        "textGenerationConfig": {
                            "maxTokenCount": 10,
                            "temperature": 0.1
                        }
                    }
                elif 'llama' in model_id:
                    body = {
                        "prompt": "Test",
                        "max_gen_len": 10,
                        "temperature": 0.1
                    }
                elif 'deepseek' in model_id:
                    body = {
                        "messages": [{"role": "user", "content": "Test"}],
                        "max_tokens": 10,
                        "temperature": 0.1
                    }
                else:
                    body = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Test"}]
                    }
                
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps(body)
                )
                
                accessible_models.append(model_id)
                print(f"   ✅ {model_id}")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_msg = e.response['Error']['Message']
                
                if 'AccessDeniedException' in error_code or 'access denied' in error_msg.lower():
                    blocked_models.append((model_id, "Access denied - request access"))
                    print(f"   🔐 {model_id} - Access denied")
                elif 'ValidationException' in error_code:
                    blocked_models.append((model_id, "Validation error - check model availability"))
                    print(f"   ❌ {model_id} - Validation error")
                else:
                    blocked_models.append((model_id, f"Error: {error_msg}"))
                    print(f"   ❌ {model_id} - {error_msg}")
        
        print(f"\n📊 Results for {region}:")
        print(f"   ✅ Accessible models: {len(accessible_models)}")
        print(f"   🔐 Need access request: {len([m for m, r in blocked_models if 'Access denied' in r])}")
        print(f"   ❌ Other errors: {len([m for m, r in blocked_models if 'Access denied' not in r])}")
        
        return accessible_models, blocked_models
        
    except Exception as e:
        print(f"   ❌ Failed to test {region}: {e}")
        return [], []

def show_model_access_instructions():
    """Show instructions for requesting Bedrock model access with DeepSeek priority"""
    print("\n" + "="*75)
    print("🚀 HOW TO REQUEST BEDROCK MODEL ACCESS (DeepSeek Priority)")
    print("="*75)
    
    print("\n1. 🌐 Open AWS Console:")
    print("   https://console.aws.amazon.com/bedrock/")
    
    print("\n2. 📍 Navigate to Model Access:")
    print("   • In the left sidebar, click 'Model access'")
    print("   • Or go directly: Bedrock > Base models > Model access")
    
    print("\n3. 🔍 Find and Request These Models (Priority Order):")
    
    print("\n   🤖 PRIORITY 1 - DeepSeek Models (us-east-1 On-Demand):")
    print("     ✅ DeepSeek V2.5 Chat (general purpose)")
    print("     ✅ DeepSeek Coder V2 Instruct (coding specialist)")
    print("     � Best for: Code generation, technical content, programming help")
    
    print("\n   �🚀 PRIORITY 2 - Nova Models (Amazon - us-east-1):")
    print("     ✅ Amazon Nova Micro (fast, cheap)")
    print("     ✅ Amazon Nova Lite (balanced)")  
    print("     ✅ Amazon Nova Pro (most capable)")
    
    print("\n   🦙 PRIORITY 3 - Llama Models (Meta - us-east-1):")
    print("     ✅ Llama 3.2 1B Instruct (fastest)")
    print("     ✅ Llama 3.2 3B Instruct (balanced)")
    print("     ✅ Llama 3.2 11B Instruct (good performance)")
    print("     • Llama 3.1 8B Instruct (alternative)")
    print("     • Llama 3.1 70B Instruct (high quality)")
    
    print("\n    FALLBACK - Claude Models (Anthropic):")
    print("     • Claude 3.5 Sonnet (latest)")
    print("     • Claude 3 Haiku (fast, cheap)")
    
    print("\n4. 📝 Request Access Process:")
    print("   • Click 'Request model access' or 'Manage model access'")
    print("   • Select ALL the models you want (recommended)")
    print("   • Fill out the use case form:")
    print("     - Use case: 'AI-powered content generation and coding assistance'")
    print("     - Company: Your organization name")
    print("     - Details: 'Building lipsync video generator with AI narration and DeepSeek for code generation'")
    
    print("\n5. ⏱️ Approval Timeline:")
    print("   • DeepSeek models: Usually instant to 30 minutes ⚡")
    print("   • Nova models: Usually instant to 15 minutes")
    print("   • Llama models: Usually instant to 30 minutes") 
    print("   • Claude models: Usually instant")
    print("   • You'll get email notifications for each approval")
    
    print("\n6. 🧪 After Approval:")
    print("   • Run this script again to verify access")
    print("   • Test in your Flask application")
    print("   • Models will appear as 'Access granted' in console")
    
    print("\n💡 Pro Tips:")
    print("   • Request ALL models at once - no extra cost")
    print("   • DeepSeek models excel at coding and technical tasks")
    print("   • Use On-Demand throughput for cost-effective testing")
    print("   • us-east-1 has the most comprehensive model selection")
    print("   • You only pay for what you use (per token)")
    
    print("\n🎯 Recommended Selection for Your Use Case:")
    print("   ✅ DeepSeek V2.5 Chat (primary - excellent for all tasks)")
    print("   ✅ DeepSeek Coder V2 Instruct (coding specialist)")
    print("   ✅ Amazon Nova Micro (backup - fast & cheap)")
    print("   ✅ Llama 3.2 3B Instruct (alternative general purpose)")
    print("   ✅ Claude 3 Haiku (reliable fallback)")
    
    print("\n🌟 Why DeepSeek for Your Project:")
    print("   • Superior code generation capabilities")
    print("   • Excellent technical documentation")
    print("   • Great for video script generation")
    print("   • Cost-effective On-Demand pricing")
    print("   • Available in us-east-1 with full features")

def check_regions():
    """Check Bedrock availability across regions with On-Demand throughput"""
    print("\n🌍 Checking Bedrock availability across regions (On-Demand models)...")
    
    regions_to_test = [
        ('us-east-1', 'North Virginia - Primary for Nova, Llama, DeepSeek'),
        ('ap-southeast-1', 'Singapore - Claude, Titan available'),
        ('us-west-2', 'Oregon - Alternative region')
    ]
    
    for region, description in regions_to_test:
        print(f"\n📍 {region} ({description}):")
        regional_models = get_models_for_region(region)
        
        if not regional_models:
            print(f"   ⚠️ No model data for {region}")
            continue
            
        accessible, blocked = test_model_access(region)
        
        # Show what's expected to be available
        total_expected = sum(len(models) for models in regional_models.values())
        print(f"   📊 Expected models: {total_expected}")
        
        for family, models in regional_models.items():
            print(f"   📦 {family.upper()}: {len(models)} models")
            for model in models[:2]:  # Show first 2
                print(f"      • {model}")
        
        if accessible:
            print(f"   ✅ {len(accessible)} accessible / {total_expected} expected")
        else:
            print(f"   🔐 Need to request access for all {total_expected} models")

def main():
    print("🤖 AWS Bedrock Nova Model Access Helper")
    print("="*50)
    
    # Check current configuration
    print(f"\n📋 Current configuration:")
    print(f"   Primary Bedrock region: {AWS_REGIONS['bedrock']}")
    print(f"   Models to test: {len(get_bedrock_models())}")
    
    # Test current region
    accessible, blocked = test_model_access(AWS_REGIONS['bedrock'])
    
    # Check if we need to request access
    nova_blocked = [m for m, r in blocked if 'nova' in m.lower() and 'Access denied' in r]
    llama_blocked = [m for m, r in blocked if 'llama' in m.lower() and 'Access denied' in r]
    deepseek_blocked = [m for m, r in blocked if 'deepseek' in m.lower() and 'Access denied' in r]
    
    total_blocked = len(nova_blocked) + len(llama_blocked) + len(deepseek_blocked)
    
    if total_blocked > 0:
        print(f"\n🔐 Models needing access approval:")
        if nova_blocked:
            print(f"   • Nova models: {len(nova_blocked)}")
        if llama_blocked:
            print(f"   • Llama models: {len(llama_blocked)}")
        if deepseek_blocked:
            print(f"   • DeepSeek models: {len(deepseek_blocked)}")
        show_model_access_instructions()
    
    if accessible:
        print(f"\n🎉 You have access to {len(accessible)} models!")
        print("   Your application should work with Bedrock.")
    else:
        print(f"\n⚠️ No models accessible in {AWS_REGIONS['bedrock']}")
        print("   You need to request model access.")
        
    # Test other regions
    print(f"\n🔄 Checking other regions...")
    check_regions()
    
    print(f"\n✅ Done! Next steps:")
    if total_blocked > 0:
        print("   1. Request model access in AWS Console (all models at once)")
        print("   2. Wait for approval (usually very quick)")
        print("   3. Run your application again")
        print("   4. Priority: Nova Micro → Llama 3.2 3B → DeepSeek V2.5")
    else:
        print("   1. Your Bedrock setup looks good!")
        print("   2. Run your Flask app to test")

if __name__ == "__main__":
    main()
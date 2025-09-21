#!/usr/bin/env python3
"""
Test AWS services in different regions
Run this to check which regions work for your account/permissions
"""

from aws_config import print_region_info
import boto3
import json

def test_service_in_region(service_name, region, test_func):
    """Test a specific service in a specific region"""
    try:
        result = test_func(region)
        print(f"✅ {service_name} in {region}: Working")
        return True
    except Exception as e:
        print(f"❌ {service_name} in {region}: {str(e)[:80]}...")
        return False

def test_translate_region(region):
    """Test AWS Translate in a specific region"""
    client = boto3.client('translate', region_name=region)
    return client.translate_text(
        Text="Hello",
        SourceLanguageCode='en', 
        TargetLanguageCode='es'
    )

def test_bedrock_region(region):
    """Test AWS Bedrock in a specific region"""
    client = boto3.client('bedrock-runtime', region_name=region)
    test_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 20,
        "messages": [{"role": "user", "content": "Hello"}]
    }
    return client.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        contentType='application/json',
        accept='application/json', 
        body=json.dumps(test_body)
    )

def test_transcribe_region(region):
    """Test AWS Transcribe in a specific region"""
    client = boto3.client('transcribe', region_name=region)
    return client.list_transcription_jobs(MaxResults=1)

def main():
    print("🧪 Testing AWS Services Across Regions")
    print("=" * 50)
    
    # Show current configuration
    print_region_info()
    print()
    
    # Test regions
    test_regions = [
        'us-east-1',      # N. Virginia (most services)
        'us-west-2',      # Oregon  
        'eu-west-1',      # Ireland
        'ap-southeast-1', # Singapore (your current)
        'ap-southeast-2', # Sydney
    ]
    
    services_to_test = [
        ('Transcribe', test_transcribe_region),
        ('Translate', test_translate_region), 
        ('Bedrock', test_bedrock_region),
    ]
    
    print("🌍 Testing Services by Region:")
    print("-" * 30)
    
    results = {}
    for region in test_regions:
        print(f"\n📍 Testing {region}:")
        results[region] = {}
        
        for service_name, test_func in services_to_test:
            working = test_service_in_region(service_name, region, test_func)
            results[region][service_name] = working
    
    # Summary
    print("\n📊 Summary - Working Services by Region:")
    print("-" * 40)
    for region, services in results.items():
        working_services = [svc for svc, works in services.items() if works]
        if working_services:
            print(f"✅ {region}: {', '.join(working_services)}")
        else:
            print(f"❌ {region}: No services working")
    
    # Recommendations
    print("\n💡 Recommendations:")
    print("-" * 20)
    
    # Find best regions for each service
    for service_name, _ in services_to_test:
        working_regions = [region for region, services in results.items() 
                         if services.get(service_name, False)]
        if working_regions:
            print(f"🎯 {service_name}: Use {working_regions[0]} (alternatives: {', '.join(working_regions[1:])})")
        else:
            print(f"⚠️ {service_name}: No working regions found - check permissions")

if __name__ == "__main__":
    main()
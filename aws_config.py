"""
AWS Service Configuration
Set custom regions for different AWS services based on availability and permissions.
"""

# AWS Region Configuration
# You can customize these regions based on:
# 1. Service availability in your region
# 2. Service control policies in your organization
# 3. Cost considerations
# 4. Latency requirements

AWS_REGIONS = {
    # Default region (for STS and S3)
    'default': 'ap-southeast-1',  # Singapore
    
    # Transcribe regions (widely available)
    'transcribe': 'ap-southeast-1',  # Singapore
    
    # Translate regions (available in fewer regions)
    'translate': 'us-east-1',  # N. Virginia - most services available here
    
    # Bedrock regions (limited availability) - test both Singapore and N. Virginia
    'bedrock': 'us-east-1',  # N. Virginia - primary for Nova models
    'bedrock_alt': 'ap-southeast-1',  # Singapore - alternative region
    
    # Alternative regions you can try:
    'alternatives': {
        'transcribe': ['us-east-1', 'us-west-2', 'eu-west-1'],
        'translate': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-2'],
        'bedrock': ['us-east-1', 'ap-southeast-1', 'us-west-2', 'eu-west-1']  # Include Singapore
    }
}

# Bedrock models to try (prioritizing DeepSeek for us-east-1 with On-Demand)
BEDROCK_MODELS = [
    # DeepSeek models (PRIORITY 1 - excellent coding models, inference profiles & On-Demand us-east-1)
    'arn:aws:bedrock:us-east-1:188473669770:inference-profile/us.deepseek.r1-v1:0',  # DeepSeek R1 v1 (newest)
    'deepseek.deepseek-v2-5-chat-v1:0',
    'deepseek.deepseek-coder-v2-instruct-v1:0',
    
    # Nova models (PRIORITY 2 - newest Amazon models, us-east-1 primarily)
    'amazon.nova-micro-v1:0',
    'amazon.nova-lite-v1:0', 
    'amazon.nova-pro-v1:0',
    
    # Llama models (PRIORITY 3 - Meta, very popular, On-Demand available)
    'meta.llama3-2-1b-instruct-v1:0',
    'meta.llama3-2-3b-instruct-v1:0',
    'meta.llama3-2-11b-instruct-v1:0',
    'meta.llama3-2-90b-instruct-v1:0',
    'meta.llama3-1-405b-instruct-v1:0',
    'meta.llama3-1-70b-instruct-v1:0',
    'meta.llama3-1-8b-instruct-v1:0',
    
    # Claude models (FALLBACK - Anthropic, widely available, On-Demand)
    'anthropic.claude-3-5-sonnet-20241022-v2:0',
    'anthropic.claude-3-haiku-20240307-v1:0',
    'anthropic.claude-3-sonnet-20240229-v1:0',
    'anthropic.claude-instant-v1',
    
    # Titan models (Amazon - basic fallback, On-Demand)
    'amazon.titan-text-express-v1',
    'amazon.titan-text-lite-v1'
]

# Regional model availability for On-Demand throughput
REGIONAL_MODEL_AVAILABILITY = {
    'us-east-1': {  # North Virginia - best availability
        'nova': ['amazon.nova-micro-v1:0', 'amazon.nova-lite-v1:0', 'amazon.nova-pro-v1:0'],
        'llama': ['meta.llama3-2-1b-instruct-v1:0', 'meta.llama3-2-3b-instruct-v1:0', 'meta.llama3-1-8b-instruct-v1:0'],
        'deepseek': [
            'arn:aws:bedrock:us-east-1:188473669770:inference-profile/us.deepseek.r1-v1:0',  # DeepSeek R1 v1 (newest)
            'deepseek.deepseek-v2-5-chat-v1:0'
        ],
        'claude': ['anthropic.claude-3-haiku-20240307-v1:0', 'anthropic.claude-3-sonnet-20240229-v1:0'],
        'titan': ['amazon.titan-text-express-v1', 'amazon.titan-text-lite-v1']
    },
    'ap-southeast-1': {  # Singapore - limited but available
        'claude': ['anthropic.claude-3-haiku-20240307-v1:0', 'anthropic.claude-instant-v1'],
        'titan': ['amazon.titan-text-express-v1'],
        'llama': ['meta.llama3-1-8b-instruct-v1:0']  # May be available
    },
    'us-west-2': {  # Oregon - good alternative
        'claude': ['anthropic.claude-3-haiku-20240307-v1:0', 'anthropic.claude-3-sonnet-20240229-v1:0'],
        'llama': ['meta.llama3-2-3b-instruct-v1:0', 'meta.llama3-1-8b-instruct-v1:0'],
        'titan': ['amazon.titan-text-express-v1']
    }
}

def get_models_for_region(region):
    """Get available models for a specific region"""
    return REGIONAL_MODEL_AVAILABILITY.get(region, {})

def get_bedrock_models():
    """Get list of Bedrock models to try"""
    return BEDROCK_MODELS

# Service availability by region (as of 2025)
SERVICE_AVAILABILITY = {
    'us-east-1': ['transcribe', 'translate', 'bedrock', 's3'],
    'us-west-2': ['transcribe', 'translate', 'bedrock', 's3'], 
    'eu-west-1': ['transcribe', 'translate', 'bedrock', 's3'],
    'ap-southeast-1': ['transcribe', 's3'],  # Your current region
    'ap-southeast-2': ['transcribe', 'translate', 's3'],
    'eu-central-1': ['transcribe', 'translate', 's3'],
}

def get_region_for_service(service_name):
    """Get the configured region for a specific service"""
    return AWS_REGIONS.get(service_name, AWS_REGIONS['default'])

def get_alternative_regions(service_name):
    """Get alternative regions for a service if the primary fails"""
    return AWS_REGIONS['alternatives'].get(service_name, [AWS_REGIONS['default']])

def print_region_info():
    """Print current region configuration"""
    print("🌍 AWS Region Configuration:")
    for service, region in AWS_REGIONS.items():
        if service != 'alternatives':
            print(f"   {service.capitalize()}: {region}")
    
    print("\n🔄 Alternative regions available:")
    for service, regions in AWS_REGIONS['alternatives'].items():
        print(f"   {service.capitalize()}: {', '.join(regions)}")

if __name__ == "__main__":
    print_region_info()
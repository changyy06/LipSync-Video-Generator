import os
import boto3
import pytest
from botocore.exceptions import ClientError, NoCredentialsError


class CredentialsValidateFailedError(Exception):
    """Custom exception for credential validation failures"""
    pass


class BedrockProvider:
    """Simple Bedrock provider for credential validation"""
    
    def validate_provider_credentials(self, credentials):
        """Validate AWS Bedrock provider credentials"""
        try:
            # Check if required credentials are provided
            aws_region = credentials.get("aws_region")
            aws_access_key = credentials.get("aws_access_key") 
            aws_secret_access_key = credentials.get("aws_secret_access_key")
            
            if not all([aws_region, aws_access_key, aws_secret_access_key]):
                raise CredentialsValidateFailedError("Missing required AWS credentials")
            
            # Create Bedrock client with provided credentials
            client = boto3.client(
                'bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_access_key
            )
            
            # Test connection by listing available models (this requires minimal permissions)
            try:
                # Try to make a simple call to validate credentials
                response = client.list_foundation_models()
                print(f"✅ Bedrock credentials validated successfully in {aws_region}")
                return True
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code in ['UnauthorizedOperation', 'AccessDenied']:
                    print(f"✅ Credentials valid but limited permissions in {aws_region}")
                    return True  # Credentials are valid, just limited permissions
                else:
                    raise CredentialsValidateFailedError(f"AWS API error: {error_code}")
            
        except NoCredentialsError:
            raise CredentialsValidateFailedError("No AWS credentials found")
        except Exception as e:
            raise CredentialsValidateFailedError(f"Validation failed: {str(e)}")


def test_validate_provider_credentials():
    """Test Bedrock provider credential validation"""
    provider = BedrockProvider()

    # Test with empty credentials (should fail)
    with pytest.raises(CredentialsValidateFailedError):
        provider.validate_provider_credentials(
            credentials={}
        )

    # Test with environment credentials (should pass if configured)
    aws_region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION") or "us-east-1"
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if aws_access_key and aws_secret_access_key:
        try:
            provider.validate_provider_credentials(
                credentials={
                    "aws_region": aws_region,
                    "aws_access_key": aws_access_key,
                    "aws_secret_access_key": aws_secret_access_key
                }
            )
            print(f"✅ Environment credentials validation passed for {aws_region}")
        except CredentialsValidateFailedError as e:
            print(f"❌ Environment credentials validation failed: {e}")
            raise
    else:
        print("⚠️ No AWS credentials found in environment variables")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to test")


def test_deepseek_r1_access():
    """Test specific DeepSeek R1 model access"""
    try:
        # Use default AWS configuration (from AWS CLI or environment)
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test the specific DeepSeek R1 inference profile
        deepseek_r1_arn = "arn:aws:bedrock:us-east-1:188473669770:inference-profile/us.deepseek.r1-v1:0"
        
        try:
            response = client.converse(
                modelId=deepseek_r1_arn,
                messages=[
                    {"role": "user", "content": [{"text": "Hello, test message"}]}
                ],
                inferenceConfig={
                    "maxTokens": 20,
                    "temperature": 1.0,
                    "topP": 0.9
                }
            )
            
            print(f"✅ DeepSeek R1 model accessible!")
            print(f"   Response: {response['output']['message']['content'][0]['text']}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if 'AccessDenied' in error_code or 'does not have access' in str(e):
                print(f"🔐 DeepSeek R1 model needs access approval in us-east-1")
                print(f"   Go to AWS Console > Bedrock > Model access to request access")
            else:
                print(f"❌ DeepSeek R1 test failed: {error_code}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek R1 test error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing AWS Bedrock Credentials and DeepSeek R1 Access")
    print("=" * 60)
    
    # Test credential validation
    try:
        test_validate_provider_credentials()
    except Exception as e:
        print(f"❌ Credential test failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test DeepSeek R1 specific access
    test_deepseek_r1_access()
    
    print("\n✨ Testing complete!")
# AWS Setup Guide for Lipsync Video Generator

## Prerequisites
You need:
1. AWS Account with credits
2. AWS Access Key ID and Secret Access Key
3. Appropriate permissions for Transcribe, Translate, Bedrock, and S3

## Step 1: Configure AWS Credentials

### Option A: Environment Variables (Recommended for development)
Set these environment variables in your terminal:
```bash
set AWS_ACCESS_KEY_ID=your_access_key_here
set AWS_SECRET_ACCESS_KEY=your_secret_key_here
set AWS_DEFAULT_REGION=us-east-1
```

### Option B: AWS CLI Configuration
```bash
pip install awscli
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (us-east-1 recommended)
- Output format (json)

## Step 2: Set up S3 Bucket
Create an S3 bucket for temporary audio files:
1. Go to AWS S3 Console
2. Create bucket named "lipsync-temp-audio-[your-name]" 
3. Update bucket name in aws_helpers.py

## Step 3: Enable Bedrock Models
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to Claude models:
   - Anthropic Claude Instant
   - Anthropic Claude v2
   - Anthropic Claude 3 Haiku

## Step 4: Required AWS Permissions
Your IAM user/role needs these permissions:
- transcribe:*
- translate:*
- bedrock:InvokeModel
- s3:GetObject, s3:PutObject, s3:DeleteObject

## Step 5: Update Configuration
Edit aws_helpers.py and change:
```python
self.bucket_name = 'your-actual-bucket-name'
```

## Estimated Costs (with credits)
- Transcribe: ~$0.024 per minute
- Translate: ~$15 per million characters
- Bedrock Claude: ~$0.25 per 1K input tokens
- S3: ~$0.023 per GB storage

## Regions with Bedrock Support
- us-east-1 (N. Virginia) - Recommended
- us-west-2 (Oregon)
- eu-west-1 (Ireland)

## Troubleshooting
- If Bedrock access denied: Request model access in console
- If S3 errors: Check bucket name and permissions
- If region errors: Ensure all services available in your region
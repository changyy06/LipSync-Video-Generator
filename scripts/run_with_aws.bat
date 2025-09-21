@echo off
echo Setting AWS credentials...
set AWS_ACCESS_KEY_ID=" AWS_ACCESS_KEY_ID"
set AWS_SECRET_ACCESS_KEY="AWS_SECRET_ACCESS_KEY"
set AWS_DEFAULT_REGION="AWS_DEFAULT_REGION"
echo AWS credentials set!
echo.
echo Starting Flask app...
python app.py

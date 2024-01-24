#!/bin/bash

# Define variables
REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
ECR_REPOSITORY_NAME="tengri_cluster"
LAMBDA_FUNCTION_NAME="carbon_serverless"
SPECIFIC_IMAGE_TAG="latest"
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$SPECIFIC_IMAGE_TAG"

# Step 1: Build the Docker image
echo "Building Docker image..."
docker buildx build --platform linux/amd64 -f ./Dockerfile -t $LAMBDA_FUNCTION_NAME .

# Step 2: Authenticate Docker to the ECR Registry
echo "Authenticating Docker to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Step 3: Tag the Docker image with specific tag and 'latest'
echo "Tagging Docker image with specific tag..."
docker tag $LAMBDA_FUNCTION_NAME:latest $IMAGE_URI

# Step 4: Push the Docker images to ECR
echo "Pushing Docker image to ECR..."
docker push $IMAGE_URI

# Check if Lambda function already exists
function_exists=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $REGION 2>&1)

if [[ $function_exists == *"Function not found"* ]]; then
    # Step 5: Create a new Lambda function from the image
    echo "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=$IMAGE_URI \
        --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-admin \
        --region $REGION \
        --timeout 60 \
        --memory-size 128 \
        --tracing-config Mode=Active
else
    # Update the existing Lambda function
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --image-uri $IMAGE_URI \
        --region $REGION
fi

echo "Deployment complete."

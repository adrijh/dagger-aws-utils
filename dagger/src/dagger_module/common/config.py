import os


AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_DEFAULT_REGION = "eu-west-1"
ECR_REGISTRY_URI = "637387903715.dkr.ecr.eu-west-1.amazonaws.com"

LAMBDA_IMAGE = "public.ecr.aws/lambda/python:{python_version}"

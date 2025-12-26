# VehicleDesign Streamlit App Deployment Guide

This guide explains how to deploy the VehicleDesign Streamlit application using GitHub Actions for CI/CD and direct deployment to EC2.

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with ECR repository created
2. **GitHub repository** with the VehicleDesign code
3. **AWS credentials** configured in GitHub Secrets
4. **EC2 instance** running with Docker installed

## AWS Setup

### 1. Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name vehicle-design --region us-east-1

# Get login token (for manual testing)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 975050138131.dkr.ecr.us-east-1.amazonaws.com
```

### 2. Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and Variables > Actions, and add:

- `AWS_ACCESS_KEY_ID`: Your AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: `us-east-1`
- `ECR_REPOSITORY`: `vehicle-design`

## Deployment Process

### Automatic CI/CD Pipeline

The deployment happens automatically when you:

1. Push to `main` or `dev` branch
2. Create a pull request to `main` or `dev` branch

The GitHub Actions workflow will:
1. Build the Docker image
2. Tag it with the commit SHA and `latest`
3. Push to ECR repository: `975050138131.dkr.ecr.us-east-1.amazonaws.com/vehicle-design`

### Manual Deployment to EC2

After GitHub Actions pushes to ECR, deploy to your EC2 instance:

```bash
# First time setup (copy docker-compose.yml to EC2)
cd deploy
make setup-remote

# Deploy to EC2
make deploy

# Or deploy locally for testing
make deploy-local
```

### Local Development

For local development and testing:

```bash
# Using docker-compose (recommended)
docker-compose up --build

# Or build and run manually
docker build -t vehicle-design .
docker run -p 8502:8502 vehicle-design
```

## Current Infrastructure

### EC2 Deployment Architecture

The application is deployed to an existing EC2 instance using docker-compose:

- **EC2 Host**: `23.20.119.96`
- **Container Name**: `vehicle-design-app`
- **Port**: `8502`
- **ECR Repository**: `975050138131.dkr.ecr.us-east-1.amazonaws.com/vehicle-design`

### Deployment Commands

The Makefile provides three deployment targets:

```bash
# Setup remote EC2 (first time only)
make setup-remote

# Deploy to production EC2
make deploy

# Deploy locally for development
make deploy-local
```

### Manual Container Management

If needed, you can manage the container manually on EC2:

```bash
# SSH to EC2 instance
ssh -i credentials/MilvusKeyPair.pem ec2-user@23.20.119.96

# Check running containers
sudo docker ps

# View logs
sudo docker logs vehicle-design-app

# Stop/start services
sudo docker-compose down
sudo docker-compose up -d
```

## Environment Variables

### Docker Configuration

The following environment variables are configured in the Dockerfile and docker-compose.yml:

- `STREAMLIT_SERVER_PORT=8502`: Port for Streamlit server
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`: Listen on all interfaces
- `STREAMLIT_SERVER_HEADLESS=true`: Run without browser
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`: Disable analytics

### Production Environment Variables

For production deployment, the following are set via the Makefile:

- `AWS_ACCESS_KEY_ID`: AWS credentials for ECR access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `IMAGE_URI`: Full ECR image URI (production only)

### Docker Compose Behavior

- **Local Development**: When `IMAGE_URI` is not set, builds locally using `build: .`
- **Production**: When `IMAGE_URI` is set, pulls from ECR repository

## Health Checks

The container includes a health check endpoint at `/_stcore/health` that can be used for:
- Load balancer health checks
- Container orchestration health monitoring
- Automated restart policies

## Troubleshooting

### Common Issues

1. **ECR Repository doesn't exist**: Create it with `aws ecr create-repository --repository-name vehicle-design --region us-east-1`
2. **GitHub Actions fails**: Check that all GitHub secrets are set correctly
3. **Container won't start**: Verify port 8502 is not already in use on EC2
4. **App not accessible**: Ensure EC2 security groups allow traffic on port 8502
5. **SSH connection fails**: Check that `credentials/MilvusKeyPair.pem` exists and has correct permissions

### Debugging Commands

```bash
# Check GitHub Actions workflow status
# Go to your GitHub repo → Actions tab

# SSH to EC2 and check logs
ssh -i credentials/MilvusKeyPair.pem ec2-user@23.20.119.96
sudo docker logs vehicle-design-app

# Check if container is running
sudo docker ps

# Check docker-compose status
sudo docker-compose ps

# View ECR repository
aws ecr describe-repositories --repository-names vehicle-design --region us-east-1
```

## Security Considerations

- The container runs as a non-root user (`streamlit`)
- AWS credentials are passed as environment variables (consider using IAM roles for better security)
- SSH key (`MilvusKeyPair.pem`) should have restricted permissions (`chmod 600`)
- EC2 security groups should only allow necessary ports (22 for SSH, 8502 for app)
- Consider using AWS Secrets Manager instead of hardcoded credentials in Makefile

## Application Access

Once deployed, the application is accessible at:
- **Production**: `http://23.20.119.96:8502`
- **Local Development**: `http://localhost:8502`

## File Structure

```
VehicleDesign/
├── docker-compose.yml          # Single compose file for local and production
├── Dockerfile                  # Container definition
├── deploy/
│   └── Makefile               # Deployment commands
├── .github/workflows/
│   └── deploy.yml             # CI/CD pipeline
└── credentials/
    └── MilvusKeyPair.pem      # SSH key for EC2 access
```

## Quick Start

1. **Setup GitHub Secrets** (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, ECR_REPOSITORY)
2. **Create ECR Repository**: `aws ecr create-repository --repository-name vehicle-design --region us-east-1`
3. **Push Code**: Triggers GitHub Actions to build and push to ECR
4. **Deploy**: `cd deploy && make setup-remote && make deploy`
5. **Access**: Visit `http://23.20.119.96:8502`

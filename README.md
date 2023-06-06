# TODO: Project Name

## Overview

TODO: Add

## Prerequisites

- Basic understanding of Python
- Ability to deploy AWS Cloud Development Kit (AWS CDK)
- TODO: Add

## How It Works

TODO: Add

## Deployment

There are multiple ways to deploy this application. You can deploy the stack directly using `cdk deploy <Stack>` or deploy CI/CD pipeline stack which will deploy the application

### Individual Stack Deployment
To deploy the application directly, ideally to development environment

First, create the ECR repository
```sh
npx cdk deploy Repository
```

Then login to the repository
```sh
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com
```

Build your container image
```sh
docker build -t sample-app:latest .
```

Tag your container image
```sh
docker tag sample-app:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/sample-app:latest
```

Push your container image to ECR
```sh
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/sample-app:latest
```

Deploy the Backed stack
```sh
npx cdk deploy Backend
```

### Pipeline Deployment

To deploy the application via CI/CD. This will create 

```sh
npx cdk deploy Pipeline
```

Push the code to the codecommit repository
```
git remote add codecommit <codecommit::url>
git push codecommit main
```

### Cleanup

TODO: Add

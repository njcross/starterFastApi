🏗 How to set up EC2 & EKS (step-by-step)

Here’s a practical guide to spinning up EC2 + EKS for your application.

Part 1: Set up EC2 (if choosing self-host / Docker Compose)

This is if you skip Kubernetes and run everything on a VM. (Optional)

Launch an EC2 instance

Choose AMI: Amazon Linux 2023 or Ubuntu

Instance type: t3.large or t3.medium for dev

Attach security group: allow SSH (22), HTTP (80), HTTPS (443)

Attach an EBS volume (e.g. 100 GB)

SSH into instance

sudo dnf update -y    # or apt update / apt upgrade
sudo dnf install -y docker
sudo systemctl enable --now docker


Install Docker Compose plugin

mkdir -p ~/.docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/download/v2.X.Y/docker-compose-linux-x86_64" \
  -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose


Clone your project and start containers

git clone <your repo>
cd repo/compose
# set proper .env
docker compose up -d


Optional: install Nginx or Certbot if you want HTTPS directly on this EC2 rather than using ALB.

Part 2: Set up EKS + run Kubernetes

This is recommended for scalability, auto-healing, etc.

Prerequisites

AWS CLI & eksctl installed and configured

IAM permissions to create EKS, node groups, roles, VPC resources

Steps

Create EKS cluster (control plane + VPC + IAM roles)
Using eksctl:

eksctl create cluster \
  --name myapp-cluster \
  --region us-east-1 \
  --version 1.30 \
  --nodegroup-name ng-default \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --node-type t3.large \
  --with-oidc


This sets up a VPC, subnets, IAM roles, and a managed node group.

Configure kubectl to use the new cluster:

eksctl utils write-kubeconfig --cluster=myapp-cluster --region=us-east-1


Install ALB Ingress Controller (AWS Load Balancer Controller) to manage ALBs automatically

eksctl create iamserviceaccount \
  --cluster myapp-cluster \
  --namespace kube-system \
  --name aws-load-balancer-controller \
  --attach-policy-arn arn:aws:iam::AWS_ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=myapp-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller


Deploy your application via Kubernetes manifests (Deployment, Service, Ingress)

Use Ingress annotated with alb.ingress.kubernetes.io/certificate-arn for HTTPS

Service will target pods

Deployment runs your containers

DNS & ACM certificate

Request ACM certificate for your domain (see prior instructions)

Use DNS validation via Route 53 or your DNS provider

In your Ingress manifest, reference the certificate ARN so ALB is set up with HTTPS

Test access

After DNS propagation, access https://your-domain.com

Use kubectl get ingress to inspect ALB details

1) Create an EKS cluster and node group

Using eksctl (simplest):

# install eksctl if needed: https://eksctl.io/introduction/installation/
eksctl create cluster \
  --name yourapp-dev \
  --region $AWS_REGION \
  --version 1.30 \
  --nodegroup-name ng-1 \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --node-type t3.large \
  --with-oidc


This creates:

An EKS control plane

A managed node group (EC2 worker nodes)

OIDC provider (needed for IAM roles for service accounts)

2) (Optional but common) Create ECR repos

If you want to use ECR:

aws ecr create-repository --repository-name yourapp-web --region $AWS_REGION
aws ecr create-repository --repository-name yourapp-frontend --region $AWS_REGION


Grant your node group role permission to pull from ECR. Easiest: attach the AWS-managed policy AmazonEC2ContainerRegistryReadOnly to the node group role (the role attached to your node instances). With managed node groups, the default instance profile typically already includes this; if not:

# Find the node group role
aws iam list-roles | jq -r '.Roles[] | select(.RoleName|test("eksctl-yourapp-dev.*NodeInstanceRole")).RoleName'

# Attach read-only pull permissions
aws iam attach-role-policy \
  --role-name <NODE_INSTANCE_ROLE_NAME> \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

3) Build & push images (to ECR or your chosen registry)

If ECR:

aws ecr get-login-password --region $AWS_REGION \
| docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Backend
docker build -f docker/web.Dockerfile -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-web:dev .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-web:dev

# Frontend
docker build -f docker/frontend.dev.Dockerfile -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-frontend:dev .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-frontend:dev


Using Docker Hub or GHCR instead? Just docker login to that registry and push there, then update your kustomize manifests to point at those image names.

4) Ingress & runtime add-ons

Typical stack:

AWS Load Balancer Controller (ALB Ingress)

ExternalDNS (optional: manages Route53)

cert-manager (optional: TLS via Let’s Encrypt)

Install ALB controller (once per cluster):

# Create an IAM policy for ALB controller
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Create a service account with IRSA
eksctl create iamserviceaccount \
  --cluster yourapp-dev \
  --namespace kube-system \
  --name aws-load-balancer-controller \
  --attach-policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --overwrite \
  --approve

# Install the controller (Helm)
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=yourapp-dev \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

5) Deploy your app

Update your k8s/overlays/dev with the image URIs (ECR or other registry). Then:

kubectl apply -k k8s/overlays/dev


Once the ALB Ingress is created, it will give you a DNS name. Point your domain (Route53 or your DNS provider) to it.

Single EC2 instance with Docker Compose (quickest to start)

If you just want “one box runs all containers”:

1) Launch an EC2 instance

AMI: Amazon Linux 2023 (or Ubuntu 22.04)

Size: t3.medium+ (depends on your workload)

Security Group:

Inbound: TCP 80 (HTTP), 443 (HTTPS) if you’ll terminate TLS here

Optional: 8025 (if you want Mailhog UI reachable), 22 (SSH) from your IP

Disk: 30–50 GB gp3 is typical

2) Install Docker & Compose plugin

Amazon Linux 2023:

sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker

# Compose plugin
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
  -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

docker compose version

3) Pull your code & run
# on the EC2 instance
git clone https://github.com/yourorg/yourapp.git
cd yourapp/compose

# copy or create .env.dev (or .env.prod)
# Ensure DATABASE_URL, REDIS_URL, EMAIL_MODE/SMTP*, BACKEND_PUBLIC_URL, FRONTEND_URL are set appropriately.

docker compose up -d


The web service (FastAPI) will listen on port 8000 on the instance (port mapping is in your compose files).

The frontend dev server (Vite) listens on 5173 in dev, or you can use the Nginx container in your prod Dockerfile to serve static assets on port 80.

Mailhog UI on :8025 if you keep it exposed.

4) Add HTTPS (optional but recommended)

Easiest path with a single instance:

Put Nginx or Caddy in front of your containers and use Let’s Encrypt.

Or attach the instance to an Application Load Balancer with an ACM certificate, forward 80/443 to the instance’s port 80.

Single EC2 instance with Docker Compose (quickest to start)

If you just want “one box runs all containers”:

1) Launch an EC2 instance

AMI: Amazon Linux 2023 (or Ubuntu 22.04)

Size: t3.medium+ (depends on your workload)

Security Group:

Inbound: TCP 80 (HTTP), 443 (HTTPS) if you’ll terminate TLS here

Optional: 8025 (if you want Mailhog UI reachable), 22 (SSH) from your IP

Disk: 30–50 GB gp3 is typical

2) Install Docker & Compose plugin

Amazon Linux 2023:

sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker

# Compose plugin
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
  -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

docker compose version

3) Pull your code & run
# on the EC2 instance
git clone https://github.com/yourorg/yourapp.git
cd yourapp/compose

# copy or create .env.dev (or .env.prod)
# Ensure DATABASE_URL, REDIS_URL, EMAIL_MODE/SMTP*, BACKEND_PUBLIC_URL, FRONTEND_URL are set appropriately.

docker compose up -d


The web service (FastAPI) will listen on port 8000 on the instance (port mapping is in your compose files).

The frontend dev server (Vite) listens on 5173 in dev, or you can use the Nginx container in your prod Dockerfile to serve static assets on port 80.

Mailhog UI on :8025 if you keep it exposed.

4) Add HTTPS (optional but recommended)

Easiest path with a single instance:

Put Nginx or Caddy in front of your containers and use Let’s Encrypt.

Or attach the instance to an Application Load Balancer with an ACM certificate, forward 80/443 to the instance’s port 80.
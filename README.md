# Flask + Redis + Postgres → Docker Compose → AWS ECR/EKS (Kustomize + GitHub Actions)

## Quickstart (local)

```bash
cd compose
docker compose --env-file .env.dev up --build
# visit: http://localhost:5173/
```
## on windows if docker isnt running or errors occur use these steps
1) Start the Docker Linux engine

In PowerShell (Admin):

# Start Docker Desktop service if it's stopped
Start-Service com.docker.service -ErrorAction SilentlyContinue

# Launch Docker Desktop app (if not already running)
& "C:\Program Files\Docker\Docker\Docker Desktop.exe"


Then verify the daemon is alive:

docker info
docker version
docker context ls


You should see a context like desktop-linux or default and no errors from docker info.

If you’re in Windows containers mode

Right-click the Docker whale icon in the tray → Switch to Linux containers… (Redis/Postgres images are Linux).

If WSL isn’t set up (common cause)

In PowerShell (Admin):

wsl --install
wsl --set-default-version 2
# Reboot if prompted, then:
wsl -l -v              # confirm you have a running distro (e.g., Ubuntu, VERSION 2)


Open Docker Desktop → Settings → Resources → WSL integration and enable your distro (e.g., Ubuntu-22.04).

After these steps, docker info should work. If not, reboot and try again.

2) Pull a simple image to confirm
docker pull hello-world
docker run --rm hello-world
docker pull redis:7

## Build & push to ECR

```bash
make docker-build docker-push
```

## Deploy to EKS (after EKS & IAM setup)

```bash
kubectl apply -k k8s/overlays/dev
```

## GitHub Actions CI/CD
In GitHub → Settings → Secrets and variables:

Variables

AWS_REGION, AWS_ACCOUNT_ID, ECR_REPOSITORY (e.g., yourapp-web)

EKS_CLUSTER_NAME, K8S_NAMESPACE (e.g., yourapp)

Secrets

AWS_ROLE_TO_ASSUME (IAM role with OIDC trust)

The workflow replaces REPLACEME_ECR_URI in the Deployment at apply-time, so you don’t need to commit image tags.
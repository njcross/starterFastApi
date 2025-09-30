# 🚀 Quickstart (Local Development)

This project has both a **Flask backend** and a **React + TypeScript frontend** running via Docker Compose.  
You can also run the frontend directly with Node for faster local iteration.

---

## 🖥️ macOS Setup

1. **Install Docker Desktop (Mac)**
   - Download from https://www.docker.com/products/docker-desktop/
   - Ensure it’s running and set to **Linux containers** (default).

2. **Start services**
   ```sh
   cd compose
   docker compose --env-file .env.dev up --build
   ```

3. **Access the apps**
   - Backend: [http://localhost:8000/health](http://localhost:8000/health)
   - Frontend: [http://localhost:5173](http://localhost:5173)

4. **Optional: run frontend outside Docker**
   ```sh
   cd frontend
   npm install
   npm run dev
   ```
   > Faster for hot reloading. Still proxies `/api` → backend in Docker.

---

## 🐳 Windows Setup

If Docker Desktop errors out, follow these steps:

1. **Start Docker Desktop service**
   ```powershell
   Start-Service com.docker.service -ErrorAction SilentlyContinue
   ```

2. **Launch Docker Desktop app**
   ```powershell
   & "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

3. **Verify daemon is running**
   ```powershell
   docker info
   docker version
   docker context ls
   ```

4. **Switch to Linux containers**
   - Right-click the whale → *Switch to Linux containers…*

5. **WSL 2 setup (if needed)**
   ```powershell
   wsl --install
   wsl --set-default-version 2
   wsl -l -v   # confirm VERSION = 2
   ```
   Then enable WSL integration in Docker Desktop settings.

6. **Run Compose**
   ```powershell
   cd compose
   docker compose --env-file .env.dev up --build
   ```

7. **Access the apps**
   - Backend: [http://localhost:8000/health](http://localhost:8000/health)
   - Frontend: [http://localhost:5173](http://localhost:5173)

---

## 📦 Frontend Scripts

Make sure `package.json` includes:

```json
"scripts": {
  "dev": "vite --host --port 5173",
  "build": "vite build",
  "preview": "vite preview"
}
```

---

## ☁️ Build & Push to AWS ECR

### Backend
```sh
docker build -f docker/web.Dockerfile \
  -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-web:dev .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-web:dev
```

### Frontend
```sh
docker build -f docker/frontend.dev.Dockerfile \
  -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-frontend:dev .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-frontend:dev
```

Or use `make` if available:
```sh
make docker-build docker-push
```

---

## 🚢 Deploy to AWS EKS

Once your EKS cluster and IAM role are ready:

```sh
kubectl apply -k k8s/overlays/dev
```

- Backend available at `/api/*`
- Frontend served at `/` through ALB Ingress

---

## 🔄 GitHub Actions CI/CD

Configure in **GitHub → Settings → Secrets and variables**:

### Variables
- `AWS_REGION`
- `AWS_ACCOUNT_ID`
- `ECR_REPOSITORY_WEB` (e.g. `yourapp-web`)
- `ECR_REPOSITORY_FRONTEND` (e.g. `yourapp-frontend`)
- `EKS_CLUSTER_NAME`
- `K8S_NAMESPACE`

### Secrets
- `AWS_ROLE_TO_ASSUME` (IAM role with OIDC trust)

Workflow will:
- Build Docker images (**web** + **frontend**)
- Push to ECR
- Patch k8s manifests with ECR URIs
- Apply via `kubectl -k`

---

✅ Now your README walks through **local dev (Mac & Windows)** → **Dockerized builds** → **AWS ECR/EKS deployment** → **CI/CD**.

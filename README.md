# 🚀 Quickstart (Local Development)

### Backend (Flask + Redis + Postgres)
```sh
cd compose
docker compose --env-file .env.dev up --build
```

Visit the backend health check:  
👉 http://localhost:8000/health

### Frontend (Vite + React + TypeScript)
```sh
cd frontend
npm install          # or npm ci
npm run dev          # starts Vite dev server
```

Visit the frontend app:  
👉 http://localhost:5173

> ⚡ If running inside Docker Compose, the `frontend` container also serves at `http://localhost:5173`.

Ensure `package.json` has the right scripts:
```json
"scripts": {
  "dev": "vite --host --port 5173",
  "build": "vite build",
  "preview": "vite preview"
}
```

---

# 🐳 Windows Docker Setup

If Docker isn’t running or errors occur, use these steps:

1. **Start Docker Desktop service**
   ```powershell
   Start-Service com.docker.service -ErrorAction SilentlyContinue
   ```

2. **Launch Docker Desktop app**
   ```powershell
   & "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

3. **Verify daemon**
   ```powershell
   docker info
   docker version
   docker context ls
   ```
   Should show `desktop-linux` or `default`.

4. **Switch to Linux containers**
   - Right-click the Docker whale → *Switch to Linux containers…*

5. **WSL setup (if needed)**
   ```powershell
   wsl --install
   wsl --set-default-version 2
   wsl -l -v   # confirm distro is running (e.g. Ubuntu, VERSION 2)
   ```
   Enable distro in Docker Desktop → Settings → Resources → WSL Integration.

6. **Test images**
   ```powershell
   docker pull hello-world
   docker run --rm hello-world
   docker pull redis:7
   ```

---

# ☁️ Build & Push to AWS ECR

Both **backend** and **frontend** images can be built and pushed:

```sh
# backend
docker build -f docker/web.Dockerfile -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-web:dev .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-web:dev

# frontend
docker build -f docker/frontend.dev.Dockerfile -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-frontend:dev .
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/yourapp-frontend:dev
```

Or use `make` targets if defined:
```sh
make docker-build docker-push
```

---

# 🚢 Deploy to AWS EKS

After EKS and IAM are set up:

```sh
kubectl apply -k k8s/overlays/dev
```

This applies both `web` and `frontend` Deployments/Services/Ingress.

- Backend is exposed at `/api/*`
- Frontend is served at `/` through the ALB Ingress

---

# 🔄 GitHub Actions CI/CD

In **GitHub → Settings → Secrets and variables**:

### Variables
- `AWS_REGION`
- `AWS_ACCOUNT_ID`
- `ECR_REPOSITORY_WEB` (e.g., `yourapp-web`)
- `ECR_REPOSITORY_FRONTEND` (e.g., `yourapp-frontend`)
- `EKS_CLUSTER_NAME`
- `K8S_NAMESPACE` (e.g., `yourapp`)

### Secrets
- `AWS_ROLE_TO_ASSUME` (IAM role with OIDC trust)

The CI/CD workflow will:
- Build Docker images for **web** and **frontend**
- Push to ECR
- Patch the Kubernetes manifests (`REPLACEME_ECR_URI` placeholders)
- Deploy via `kubectl apply -k k8s/overlays/dev`

---

⚡ That way your README covers **local dev → Docker → AWS ECR/EKS → CI/CD** for both parts of the app.

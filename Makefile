AWS_REGION ?= us-west-2
ACCOUNT_ID ?= 123456789012
REPO       ?= yourapp-web
TAG        ?= $(shell git rev-parse --short HEAD)
IMAGE      := $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPO):$(TAG)

docker-build:
	docker build -t $(IMAGE) -f docker/web.Dockerfile .

docker-push:
	aws ecr create-repository --repository-name $(REPO) 2>/dev/null || true
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker push $(IMAGE)

compose-dev:
	cd compose && docker compose --env-file .env.dev up --build

k8s-dev:
	kubectl apply -k k8s/overlays/dev

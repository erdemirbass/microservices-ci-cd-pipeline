.PHONY: test build scan compose-up compose-down kind-up k8s-apply

# Default IMAGE pushes to the GitHub Container Registry path for this repository.
IMAGE ?= ghcr.io/${GITHUB_REPOSITORY}
API_IMAGE ?= $(IMAGE)/api
WORKER_IMAGE ?= $(IMAGE)/worker
TAG ?= latest
K8S_NAMESPACE ?= dev
K8S_NAMESPACE_MANIFEST ?= ops/k8s/namespace.yaml
K8S_DEPLOYMENTS_DIR ?= ops/k8s/deployments
K8S_SERVICE_MANIFEST ?= ops/k8s/service.yaml
K8S_INGRESS_MANIFEST ?= ops/k8s/ingress.yaml

test:
	pip install --no-cache-dir -r services/api/requirements.txt
	pytest services/api --cov=services/api --cov-report=term-missing

build:
	docker build -f ops/docker/Dockerfile.api -t $(API_IMAGE):$(TAG) .
	docker build -f ops/docker/Dockerfile.worker -t $(WORKER_IMAGE):$(TAG) .

scan:
	./ops/security/trivy.sh $(API_IMAGE):$(TAG)
	./ops/security/trivy.sh $(WORKER_IMAGE):$(TAG)

compose-up:
	docker compose -f ops/compose/docker-compose.yml up -d

compose-down:
	docker compose -f ops/compose/docker-compose.yml down

kind-up:
	@if ! kind get clusters | grep -w $(K8S_NAMESPACE) >/dev/null 2>&1; then \
		kind create cluster --name $(K8S_NAMESPACE); \
	else \
		echo "kind cluster '$(K8S_NAMESPACE)' already exists"; \
	fi
	@kubectl get namespace $(K8S_NAMESPACE) >/dev/null 2>&1 || kubectl create namespace $(K8S_NAMESPACE)

k8s-apply:
	@if [ -f $(K8S_NAMESPACE_MANIFEST) ]; then \
		kubectl apply -f $(K8S_NAMESPACE_MANIFEST); \
	else \
		echo "Skipping namespace apply; $(K8S_NAMESPACE_MANIFEST) not found"; \
	fi
	@if [ -d $(K8S_DEPLOYMENTS_DIR) ]; then \
		kubectl apply -f $(K8S_DEPLOYMENTS_DIR); \
	else \
		echo "Skipping deployments apply; $(K8S_DEPLOYMENTS_DIR) not found"; \
	fi
	@if [ -f $(K8S_SERVICE_MANIFEST) ]; then \
		kubectl apply -f $(K8S_SERVICE_MANIFEST); \
	else \
		echo "Skipping service apply; $(K8S_SERVICE_MANIFEST) not found"; \
	fi
	@if [ -f $(K8S_INGRESS_MANIFEST) ]; then \
		kubectl apply -f $(K8S_INGRESS_MANIFEST); \
	else \
		echo "Skipping ingress apply; $(K8S_INGRESS_MANIFEST) not found"; \
	fi

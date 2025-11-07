.PHONY: test build scan compose-up compose-down kind-up k8s-apply

# Default IMAGE pushes to the GitHub Container Registry path for this repository.
IMAGE ?= ghcr.io/${GITHUB_REPOSITORY}
API_IMAGE ?= $(IMAGE)/api
WORKER_IMAGE ?= $(IMAGE)/worker
TAG ?= latest
KIND_CLUSTER ?= dev
K8S_NAMESPACE ?= dev
K8S_NAMESPACE_MANIFEST ?= ops/k8s/namespace.yaml
K8S_DEPLOYMENTS_DIR ?= ops/k8s/deployments
K8S_SERVICE_MANIFEST ?= ops/k8s/services/service-api.yaml
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
	python ops/k8s/kind_up.py $(KIND_CLUSTER) $(K8S_NAMESPACE)

k8s-apply:
	python ops/k8s/apply_manifests.py \
		$(K8S_NAMESPACE_MANIFEST) \
		$(K8S_DEPLOYMENTS_DIR) \
		$(K8S_SERVICE_MANIFEST) \
		$(K8S_INGRESS_MANIFEST)

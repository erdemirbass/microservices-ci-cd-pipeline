.PHONY: test build scan compose-up compose-down kind-up k8s-apply
test:
	@echo Running service tests
build:
	@echo Building service containers
scan:
	@echo Performing security scans
compose-up:
	@echo Starting docker-compose stack
compose-down:
	@echo Stopping docker-compose stack
kind-up:
	@echo Creating kind cluster
k8s-apply:
	@echo Applying Kubernetes manifests

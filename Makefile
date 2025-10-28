# Makefile for Llama Languages project

# ==============================================================================
# Variables
# ==============================================================================
IMAGE_NAME ?= llama-languages
DOCKER_PORT ?= 8010
PODMAN_PORT ?= 8010
CONTAINER_PORT = 8010
DATA_VOLUME = $(CURDIR)/data:/app/data

.DEFAULT_GOAL := help
.PHONY: help build-docker run-docker up-docker build-podman run-podman up-podman

# ==============================================================================
# Help
# ==============================================================================
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==============================================================================
# Docker Commands
# ==============================================================================

build-docker: ## Builds the Docker image.
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build -t $(IMAGE_NAME) .

run-docker: ## Runs the application in a Docker container.
	@echo "Running Docker container on http://localhost:$(DOCKER_PORT)"
	docker run --rm -p $(DOCKER_PORT):$(CONTAINER_PORT) -v $(DATA_VOLUME) $(IMAGE_NAME)

up-docker: build-docker run-docker ## Builds and runs the Docker container.

# ==============================================================================
# Podman Commands
# ==============================================================================

build-podman: ## Builds the Podman image.
	@echo "Building Podman image: $(IMAGE_NAME)"
	podman build -t $(IMAGE_NAME) .

run-podman: ## Runs the application in a Podman container.
	@echo "Running Podman container on http://localhost:$(PODMAN_PORT)"
	podman run --rm -p $(PODMAN_PORT):$(CONTAINER_PORT) -v $(DATA_VOLUME) $(IMAGE_NAME)

up-podman: build-podman run-podman ## Builds and runs the Podman container.
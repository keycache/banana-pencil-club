APP_NAME=banana-pencil-club
IMAGE?=$(APP_NAME):latest
PORT?=8501

.PHONY: help build run shell push clean prune

help:
	@echo "Common targets:"
	@echo "  make build        Build the Docker image (IMAGE=$(IMAGE))"
	@echo "  make run          Run the container mapping PORT (PORT=$(PORT))"
	@echo "  make shell        Start an interactive shell inside a fresh container"
	@echo "  make push         Push image (set REGISTRY, e.g. REGISTRY=ghcr.io/you)"
	@echo "  make clean        Remove dangling images & stopped containers for this app"
	@echo "  make prune        System prune (careful)"

build:
	docker build -t $(IMAGE) .

run: build
	docker run --rm -it -p 8080:8080 -e GEMINI_API_KEY=AIzaSyD56aV3Uthk6tjuxUzri6fhhew-fhMqIOg --name $(APP_NAME) $(IMAGE)

# 	docker run --rm -it -p $(PORT):8501 --name $(APP_NAME) $(IMAGE)

shell: build
	docker run --rm -it --entrypoint /bin/bash $(IMAGE)

push: build
ifneq (,$(REGISTRY))
	docker tag $(IMAGE) $(REGISTRY)/$(IMAGE)
	docker push $(REGISTRY)/$(IMAGE)
else
	@echo "Set REGISTRY env var to push (e.g. make push REGISTRY=ghcr.io/you)" && exit 1
endif

clean:
	# Remove stopped containers & dangling images related to APP_NAME
	-docker rm $$(docker ps -aq -f name=$(APP_NAME)) 2>/dev/null || true
	-docker rmi $$(docker images -q --filter reference='$(APP_NAME)') 2>/dev/null || true

prune:
	docker system prune -f

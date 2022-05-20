.PHONY: build push run

build:
	@python -m venv venv && . venv/bin/activate && \
	pip install -r requirements.txt && pip install -r dev-requirements.txt

# Build and push to a docker registry, e.g.
#   make push REGISTRY=registry.example.com
push:
	docker build -t bonobot . && \
	docker login ${REGISTRY} && \
	docker tag bonobot:latest ${REGISTRY}/bonobot:latest && \
	docker push ${REGISTRY}/bonobot:latest

# Run inside docker. Assumes the tokens are set in the host environment
run:
	docker build -t bonobot . && \
	docker run -p 8000 -e SLACK_API_TOKEN -e SLACK_BOT_TOKEN bonobot

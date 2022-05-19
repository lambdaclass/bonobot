.PHONY: build push

build:
	@python -m venv venv && . venv/bin/activate && \
	pip install -r requirements.txt && pip install -r dev-requirements.txt

push:
	docker build -t bonobot . && \
	docker login ${REGISTRY} && \
	docker tag bonobot:latest ${REGISTRY}/bonobot:latest && \
	docker push ${REGISTRY}/bonobot:latest

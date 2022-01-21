.PHONY: docker.build docker.push

TAG = registry.lambdaclass.com/bonobot

docker.build:
	docker build --platform linux/amd64 -t $(TAG) .

docker.push:
	docker push $(TAG)

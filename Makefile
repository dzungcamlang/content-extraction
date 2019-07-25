build-docker:
	@echo Build docker image
	# docker build --rm -t registry.gitlab.com/fi_ai/crawler-news:`cat VERSION` -t registry.gitlab.com/fi_ai/crawler-news:latest .
	docker build --rm -t registry.gitlab.com/fi_ai/crawler-news:latest .

push-docker-image:
	@echo Push Docker image to registry.gitlab.com
	# docker push registry.gitlab.com/fi_ai/crawler-news:`cat VERSION`
	docker push registry.gitlab.com/fi_ai/crawler-news:latest

build-docker-pypy:
	@echo Build docker image
	# docker build --rm -t registry.gitlab.com/fi_ai/crawler-news:`cat VERSION` -t registry.gitlab.com/fi_ai/crawler-news:pypy .
	docker build --rm -f Dockerfile.pypy -t registry.gitlab.com/fi_ai/crawler-news:pypy .

push-docker-image-pypy:
	@echo Push Docker image to registry.gitlab.com
	# docker push registry.gitlab.com/fi_ai/crawler-news:`cat VERSION`
	docker push registry.gitlab.com/fi_ai/crawler-news:pypy

clean-docker-exited-containers:
	docker rm -v `docker ps -a -q -f status=exited`

clean-none-images:
	docker rmi `docker images | grep none | awk '{print $3}'`

run-docker:
	docker run --rm \
	-e "MAGIC_BROWSER_MASTER_ENDPOINT=http://192.168.0.101:5000" \
	-p 5500:5500 \
	-e "BOOTSTRAP_SERVERS=103.234.37.70:9002" \
	-e "IS_TEST_API=1" \
	-it registry.gitlab.com/fi_ai/crawler-news:py3

run-docker-alpine:
	docker run --rm \
	-e "MAGIC_BROWSER_MASTER_ENDPOINT=http://103.234.36.16:9005" \
	-e "BOOTSTRAP_SERVERS=103.234.37.70:9002" \
	-it registry.gitlab.com/fi_ai/crawler-news:alpine

run:
	IS_TEST_API=1 MAGIC_BROWSER_MASTER_ENDPOINT=http://localhost:5000 BOOTSTRAP_SERVERS=103.234.37.70:9002 MAX_WORKER=40 python3 main.py

pypy-run:
	MAGIC_BROWSER_MASTER_ENDPOINT=http://14.161.50.51:9005 BOOTSTRAP_SERVERS=14.161.50.51:9002 pypy main.py

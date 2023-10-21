ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
IMAGE_NAME := "nonsense-sentiment-scraper"
TAG := "0.1"

build:
	docker build -t $(IMAGE_NAME):$(TAG) $(ROOT_DIR)

run-container:
	bash run_container.sh

all:
	make scraper CRAWL_LIMIT=100
	make extract
	make cluster CLUSTERS=3
	make cluster CLUSTERS=6
	make sentiment

test:
	make scraper CRAWL_LIMIT=10
	make extract
	make cluster CLUSTERS=3
	make cluster CLUSTERS=6
	make sentiment

scraper: log-directory
	python src/main.py --scraper CRAWL_LIMIT=$(CRAWL_LIMIT)

extract: log-directory
	python src/main.py --extract

cluster: log-directory
	python src/main.py --cluster

sentiment: log-directory
	python src/main.py --sentiment

log-directory:
	mkdir -p logs

clean-logs:
	rm -f logs/output.log
	
clean:
	rm -f ./logs/output.log && \
	rm -dfr ./output && \
	find . -name '*\.pyc' -delete && \
	find . -name '__pycache__' -type d -empty -delete

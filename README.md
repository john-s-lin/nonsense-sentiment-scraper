# Crawling, Clustering and Sentiment Analysis on Targeted Subdomains

## Running Instructions

This README contains instructions on how to run the pipeline from start to finish.

### Running inside a Docker container

You can build the image from the `Dockerfile` with `make build`.

Then to run the container, you can `make run-container`, which will start a container and enter into the container's bash terminal.

To get a list of available `conda` environments, run

```
conda env list
```

Then switch to the target conda environment `nss` with

```
conda activate nss
```

Then you can run the options below. Alternatively, you can run this bare metal, but you will have to ensure that the dependencies are installed.

### Running the whole project

The whole project can be run in one command:

```
make all
```

### Running on a test set of 10 crawled pages

You can run the whole project with a test set of 10 pages using:

```
make test
```

### Running the web crawler

You can run the web crawler only by providing the `CRAWL_LIMIT`

```bash
make scraper CRAWL_LIMIT=$(CRAWL_LIMIT) # User provides the crawl limit
```

### Running the text extractor

Extract the text like so:

```
make extract
```

### Running the clustering algorithms

User sets the number of clusters. If `CLUSTERS` is not provided, the default is 3.

```bash
make cluster CLUSTERS=$(CLUSTERS) # User provides the number of clusters to use
```

### Running the sentiment analysis

This will run sentiment analysis on all clustered text. If you have separate files for 3 clusters and 6 clusters, this command will compute AFINN scores for 3 and 6 clusters respectively, and store then in separate labeled output files.

```
make sentiment
```

### Cleaning up

You can clear all output and log files with one command:

```
make clean
```

## Note about scraping order

As per the docs, `Scrapy` crawls in [depth-first order](https://docs.scrapy.org/en/latest/faq.html#does-scrapy-crawl-in-breadth-first-or-depth-first-order).

You can adapt to breadth-first search (BFS) if you choose by setting these settings:

```python
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"
```

However, as noted, setting to BFS significantly reduces crawl speed as you cannot crawl concurrently. Attempt at your own risk 🤷🏻‍♂️.

# Crawling, Clustering and Sentiment Analysis on Targeted Subdomains

## Running Instructions

This README contains instructions on how to run the pipeline from start to finish.

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

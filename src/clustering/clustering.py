import json
import logging
import numpy as np

from scipy.sparse._csr import csr_matrix
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer


class TextClusterer:
    def __init__(self, n_clusters: int = 3) -> None:
        """Initializes TfidfVectorizer, KMeans and LSA dimensionality reducers

        Args:
            n_clusters (int, optional): Number of clusters. Defaults to 3.
        """
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.kmeans = KMeans(n_clusters=n_clusters, max_iter=100, random_state=0)
        self.lsa = make_pipeline(TruncatedSVD(n_components=100), Normalizer(copy=False))

    def generate_kmeans(self, tf_idf_vectors: np.ndarray) -> np.ndarray:
        """Generates k-means clustering

        Args:
            tf_idf_vectors (ndarray): Array of vectorized and dimension-reduced tf-idf vectors

        Returns:
            ndarray: Array of clustered tf-idf-vectors
        """
        return self.kmeans.fit_transform(tf_idf_vectors)

    def vectorize_text(self, raw_data: dict) -> csr_matrix:
        """Converts raw text to tf_idf vectors

        Args:
            raw_data (dict): Raw text

        Returns:
            csr_matrix: tf-idf vectors
        """
        return self.vectorizer.fit_transform([raw_data[url] for url in raw_data])

    def reduce_dimensions(self, vectorized_text: csr_matrix) -> np.ndarray:
        """Reduces dimensionality of vectorized text

        Args:
            vectorized_text (csr_matrix): vectorized text

        Returns:
            ndarray: reduced-dimension vectorized text
        """
        return self.lsa.fit_transform(vectorized_text)

    def generate_stats(self, filename: str) -> None:
        """Outputs statistics of cluster centroids and top 20 terms in centroids"""
        output_json = self._generate_stats_json(20)
        print(output_json)
        self.save_to_output_file(filename, output_json)

    def classify_documents_by_cluster(self, raw_text: dict) -> dict:
        """Generates dictionary of documents with cluster label and raw text for AFINN analysis

        Args:
            raw_text (dict): raw_text

        Returns:
            dict: raw_text with cluster label
        """
        output = {}
        doc_cluster_labels = self.kmeans.labels_

        for i, key in enumerate(raw_text):
            output[key] = {"cluster": int(doc_cluster_labels[i]), "raw": raw_text[key]}
        return output

    def save_to_output_file(self, filename: str, data: dict) -> None:
        """Saves output json to file

        Args:
            filename (str): filename
        """
        with open(filename, "w", encoding="utf-8") as file:
            output = json.dumps(data)
            file.write(output)
            logging.info(
                f"{'Cluster stats' if 'kmeans' in filename else 'Document clusters'} written to {filename}."
            )

    def get_raw_text(self, filename: str) -> dict:
        """Get raw text from file

        Args:
            filename (str): filename

        Returns:
            dict: dictionary of raw text by URL
        """
        data = {}
        try:
            with open(filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            logging.error(f"Invalid filename: {filename}")
        return data

    def _generate_stats_json(self, k: int = 10) -> dict:
        """Generates output dictionary in JSON format

        Args:
            k (int): Top k terms. Default is 10.

        Returns:
            dict: Cluster n mapped to top k terms.
        """
        num_top_terms = k
        output_json = {}

        ordered_centroids = self._generate_ordered_centroids()
        terms = self.vectorizer.get_feature_names_out()

        for i in range(self.kmeans.n_clusters):
            output_json[f"cluster_{i}"] = [
                terms[j] for j in ordered_centroids[i, :num_top_terms]
            ]
        return output_json

    def _generate_ordered_centroids(self) -> np.ndarray:
        """Generate ordered cluster centroids

        Returns:
            np.ndarray: Sorted cluster centroids
        """
        original_space_centroids = self.lsa[0].inverse_transform(
            self.kmeans.cluster_centers_
        )
        return original_space_centroids.argsort()[:, ::-1]

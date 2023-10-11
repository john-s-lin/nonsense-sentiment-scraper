import json
import logging

from afinn import Afinn


class SentimentAnalyzer:
    def __init__(self) -> None:
        self.afinn = Afinn()

    def get_labeled_text_json(self, filename: str) -> dict:
        """Gets labeled clustered text from JSON file

        Args:
            filename (str): filename

        Returns:
            dict: labeled clustered text
        """
        data = {}
        try:
            with open(filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            logging.error(f"Invalid filename: {filename}")
        return data

    def generate_afinn_scores_per_doc(self, raw_data: dict) -> dict:
        """Generates an AFINN score for each raw text

        Args:
            raw_data (dict): Labeled clustered text

        Returns:
            dict: Inplace mapping with added AFINN score
        """
        for key in raw_data:
            afinn_score = self.afinn.score(raw_data[key]["raw"])
            raw_data[key]["afinn"] = afinn_score
        return raw_data

    def generate_average_afinn_scores_per_cluster(
        self, afinn_data: dict, n_clusters: str
    ) -> dict:
        """Computes average cluster AFINN score given document AFINN scores

        Args:
            afinn_data (dict): document AFINN scores
            n_clusters (str): Number of clusters

        Returns:
            dict: Averaged cluster AFINN scores with top terms
        """
        avg_cluster_scores = {}
        top_terms_clustered = self.get_labeled_text_json(
            f"./output/kmeans_{n_clusters}_clusters.json"
        )

        # Sum up total AFINN score for each cluster and keep count of documents per cluster
        for key in afinn_data:
            cluster_num = afinn_data[key]["cluster"]
            cluster_key = f"cluster_{cluster_num}"
            if cluster_key not in avg_cluster_scores:
                avg_cluster_scores[cluster_key] = {}
                avg_cluster_scores[cluster_key]["avg_score"] = 0
                avg_cluster_scores[cluster_key]["count"] = 0
            avg_cluster_scores[cluster_key]["avg_score"] += afinn_data[key]["afinn"]
            avg_cluster_scores[cluster_key]["count"] += 1

        # Compute avg AFINN score for each cluster knowing count and total AFINN score
        # Append cluster top terms
        for cluster_key in avg_cluster_scores:
            temp_total_score = avg_cluster_scores[cluster_key]["avg_score"]
            temp_count = avg_cluster_scores[cluster_key]["count"]
            avg_cluster_scores[cluster_key]["avg_score"] = temp_total_score / temp_count
            avg_cluster_scores[cluster_key]["top_terms"] = top_terms_clustered[
                cluster_key
            ]

        return dict(sorted(avg_cluster_scores.items()))

    def save_to_output_file(self, filename: str, data: dict) -> None:
        """Saves output json to file

        Args:
            filename (str): filename
        """
        with open(filename, "w", encoding="utf-8") as file:
            output = json.dumps(data)
            file.write(output)
            logging.info(
                f"AFINN {'text' if 'text' in filename else 'cluster-averaged'} stats written to {filename}."
            )

"""Scoring system for refactor prioritization."""

from pathlib import Path
from typing import Any

import yaml


class ScoringEngine:
    """Weighted scoring for refactor priority ranking."""

    def __init__(self, rules_path: str | Path) -> None:
        """Initialize scoring engine from YAML file.

        Args:
            rules_path: Path to rules.yaml file
        """
        self.weights: dict[str, float] = {}

        try:
            with open(rules_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "weights" in config:
                    self.weights = config["weights"]
        except FileNotFoundError:
            pass

        # Default weights if not specified
        if not self.weights:
            self.weights = {
                "complexity": 0.5,
                "size": 0.3,
                "coupling": 0.2,
            }

    def score_file(
        self,
        file_data: dict[str, Any],
        dependencies: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute weighted refactor priority score for a file.

        Args:
            file_data: File analysis data from scanner
            dependencies: Dependency graph data

        Returns:
            Score dict with file, metrics, and total score
        """
        # Extract metrics
        avg_complexity = self._get_avg_complexity(file_data)
        loc = file_data.get("raw", {}).get("loc", 0)
        file_path = file_data.get("path", "")

        # Get coupling (number of imports)
        file_deps = dependencies.get(file_path, {})
        imports = file_deps.get("imports", [])
        coupling = len(imports)

        # Normalize metrics to 0-1 range
        norm_complexity = self._scale(avg_complexity, 0, 50)
        norm_size = self._scale(loc, 0, 1000)
        norm_coupling = self._scale(coupling, 0, 20)

        # Compute weighted score
        score = (
            self.weights.get("complexity", 0.5) * norm_complexity
            + self.weights.get("size", 0.3) * norm_size
            + self.weights.get("coupling", 0.2) * norm_coupling
        )

        return {
            "file": file_path,
            "complexity": avg_complexity,
            "loc": loc,
            "coupling": coupling,
            "score": round(score, 3),
        }

    def rank(self, index: dict[str, Any]) -> list[dict[str, Any]]:
        """Rank all files by refactor priority score.

        Args:
            index: Complete code index from scanner

        Returns:
            Sorted list of files with scores (highest priority first)
        """
        dependencies = index.get("dependencies", {})
        files = index.get("files", [])

        scores: list[dict[str, Any]] = []
        for file_data in files:
            score_data = self.score_file(file_data, dependencies)
            scores.append(score_data)

        # Sort by score descending
        scores.sort(key=lambda x: float(x["score"]), reverse=True)

        return scores

    def _get_avg_complexity(self, file_data: dict[str, Any]) -> float:
        """Get average complexity for a file.

        Args:
            file_data: File analysis data

        Returns:
            Average complexity value
        """
        complexity_list = file_data.get("complexity", [])
        if not complexity_list:
            return 0.0

        total = sum(c.get("complexity", 0) for c in complexity_list)
        return float(total / len(complexity_list))

    def _scale(self, value: float, min_val: float, max_val: float) -> float:
        """Scale value to 0-1 range.

        Args:
            value: Value to scale
            min_val: Minimum expected value
            max_val: Maximum expected value

        Returns:
            Scaled value between 0 and 1
        """
        if max_val == min_val:
            return 0.0

        scaled = (value - min_val) / (max_val - min_val)
        return float(max(0.0, min(1.0, scaled)))  # Clamp to 0-1

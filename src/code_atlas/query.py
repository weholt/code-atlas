"""Query API for code index with O(1) lookups."""

import json
from pathlib import Path
from typing import Any


class CodeIndex:
    """In-memory code index with fast lookup capabilities."""

    def __init__(self, index_path: str | Path) -> None:
        """Initialize code index from JSON file.

        Args:
            index_path: Path to code_index.json file
        """
        with open(index_path, encoding="utf-8") as f:
            self.data = json.load(f)

        self._build_indices()

    def _build_indices(self) -> None:
        """Build in-memory indices for O(1) lookups."""
        self._entity_index: dict[str, dict[str, Any]] = {}

        for file_data in self.data.get("files", []):
            for entity in file_data.get("entities", []):
                key = entity["name"]
                self._entity_index[key] = {
                    "file": file_data["path"],
                    "type": entity["type"],
                    "meta": entity,
                }

    def find(self, name: str) -> dict[str, Any] | None:
        """Find entity by name.

        Args:
            name: Name of class or function to find

        Returns:
            Entity information or None if not found
        """
        return self._entity_index.get(name)

    def complex(self, threshold: int = 10) -> list[dict[str, Any]]:
        """Find functions exceeding complexity threshold.

        Args:
            threshold: Minimum complexity value

        Returns:
            List of complex functions
        """
        results: list[dict[str, Any]] = []

        for file_data in self.data.get("files", []):
            for comp in file_data.get("complexity", []):
                if comp["complexity"] > threshold:
                    results.append(
                        {
                            "file": file_data["path"],
                            "function": comp["function"],
                            "complexity": comp["complexity"],
                            "lineno": comp["lineno"],
                        }
                    )

        return results

    def dependencies(self, file_path: str) -> dict[str, list[str]]:
        """Get dependencies for a file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with 'imports' and 'imported_by' lists
        """
        deps = self.data.get("dependencies", {}).get(file_path, {})
        return {
            "imports": deps.get("imports", []),
            "imported_by": deps.get("imported_by", []),
        }

    def top_complex(self, n: int = 10) -> list[dict[str, Any]]:
        """Get top N most complex functions.

        Args:
            n: Number of results to return

        Returns:
            List of most complex functions sorted by complexity descending
        """
        all_complex: list[dict[str, Any]] = []

        for file_data in self.data.get("files", []):
            for comp in file_data.get("complexity", []):
                all_complex.append(
                    {
                        "file": file_data["path"],
                        "function": comp["function"],
                        "complexity": comp["complexity"],
                        "lineno": comp["lineno"],
                    }
                )

        # Sort by complexity descending
        all_complex.sort(key=lambda x: x["complexity"], reverse=True)

        return all_complex[:n]

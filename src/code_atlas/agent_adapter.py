"""High-level agent adapter for convenient codebase queries."""

from pathlib import Path
from typing import Any

from code_atlas.query import CodeIndex
from code_atlas.rules import RuleEngine
from code_atlas.scoring import ScoringEngine


class AgentAdapter:
    """Unified interface combining query, rules, and scoring."""

    def __init__(self, root: Path, index_file: str = "code_index.json", rules_file: str = "rules.yaml") -> None:
        """Initialize agent adapter.

        Args:
            root: Workspace root directory
            index_file: Path to code index JSON
            rules_file: Path to rules YAML
        """
        self.root = root
        self.index_path = Path(index_file)
        self.rules_path = Path(rules_file)

        # Initialize components
        self.index = CodeIndex(self.index_path)
        self.rules = RuleEngine(self.rules_path) if self.rules_path.exists() else None
        self.scoring = ScoringEngine(self.rules_path) if self.rules_path.exists() else None

    def get_symbol_location(self, symbol: str) -> dict[str, Any] | None:
        """Find where a symbol is defined.

        Args:
            symbol: Class or function name

        Returns:
            Location info or None if not found
        """
        return self.index.find(symbol)

    def get_top_refactors(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top refactor priority targets.

        Args:
            limit: Number of results

        Returns:
            List of files with scores
        """
        if not self.scoring:
            return []

        rankings = self.scoring.rank(self.index.data)
        return rankings[:limit]

    def get_rule_violations(self) -> list[dict[str, Any]]:
        """Get all rule violations.

        Returns:
            List of violations
        """
        if not self.rules:
            return []

        violations: list[dict[str, Any]] = []
        for file_data in self.index.data.get("files", []):
            file_violations = self.rules.evaluate(file_data)
            violations.extend(file_violations)

        return violations

    def get_complex_functions(self, threshold: int = 10) -> list[dict[str, Any]]:
        """Find functions exceeding complexity threshold.

        Args:
            threshold: Minimum complexity

        Returns:
            List of complex functions
        """
        return self.index.complex(threshold)

    def get_dependency_hotspots(self, min_edges: int = 5) -> list[dict[str, Any]]:
        """Find files with high coupling.

        Args:
            min_edges: Minimum number of imports

        Returns:
            List of highly coupled files
        """
        hotspots: list[dict[str, Any]] = []
        dependencies = self.index.data.get("dependencies", {})

        for file_path, deps in dependencies.items():
            imports = deps.get("imports", [])
            imported_by = deps.get("imported_by", [])
            total_edges = len(imports) + len(imported_by)

            if total_edges >= min_edges:
                hotspots.append(
                    {
                        "file": file_path,
                        "imports": len(imports),
                        "imported_by": len(imported_by),
                        "total_coupling": total_edges,
                    }
                )

        # Sort by total coupling descending
        hotspots.sort(key=lambda x: int(x["total_coupling"]), reverse=True)

        return hotspots

    def get_untyped_or_poor_docs(self, min_comment_ratio: float = 0.1) -> list[dict[str, Any]]:
        """Find files with insufficient documentation.

        Args:
            min_comment_ratio: Minimum acceptable comment ratio

        Returns:
            List of poorly documented files
        """
        poor_docs: list[dict[str, Any]] = []

        for file_data in self.index.data.get("files", []):
            comment_ratio = file_data.get("comment_ratio", 0.0)
            if comment_ratio < min_comment_ratio:
                poor_docs.append(
                    {
                        "file": file_data.get("path", ""),
                        "comment_ratio": comment_ratio,
                        "loc": file_data.get("raw", {}).get("loc", 0),
                    }
                )

        # Sort by LOC descending (largest files first)
        poor_docs.sort(key=lambda x: int(x["loc"]), reverse=True)

        return poor_docs

    def summarize_state(self) -> dict[str, Any]:
        """Get compact summary of codebase state.

        Returns:
            Summary dict with key metrics
        """
        total_files = len(self.index.data.get("files", []))
        total_loc = sum(f.get("raw", {}).get("loc", 0) for f in self.index.data.get("files", []))

        complex_funcs = self.get_complex_functions(threshold=10)
        violations = self.get_rule_violations() if self.rules else []
        hotspots = self.get_dependency_hotspots(min_edges=5)

        return {
            "total_files": total_files,
            "total_loc": total_loc,
            "complex_functions": len(complex_funcs),
            "rule_violations": len(violations),
            "dependency_hotspots": len(hotspots),
            "scanned_at": self.index.data.get("scanned_at", ""),
        }

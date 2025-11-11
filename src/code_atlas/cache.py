"""Incremental caching system for skipping unchanged files."""

import hashlib
import json
from pathlib import Path


class FileCache:
    """Cache for tracking file hashes to enable incremental scans."""

    def __init__(self, cache_file: Path | str = ".code_atlas_cache.json") -> None:
        """Initialize file cache.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = Path(cache_file)
        self.cache: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def save(self) -> None:
        """Save cache to file."""
        try:
            self.cache_file.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")
        except OSError:
            pass  # Ignore write errors

    def get_hash(self, file_path: str) -> str | None:
        """Get cached hash for a file.

        Args:
            file_path: Path to file

        Returns:
            Cached hash or None if not in cache
        """
        return self.cache.get(file_path)

    def set_hash(self, file_path: str, file_hash: str) -> None:
        """Store hash for a file.

        Args:
            file_path: Path to file
            file_hash: SHA-256 hash of file contents
        """
        self.cache[file_path] = file_hash

    def remove(self, file_path: str) -> None:
        """Remove file from cache.

        Args:
            file_path: Path to file
        """
        self.cache.pop(file_path, None)

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file contents.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal hash string
        """
        try:
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        except OSError:
            return ""

    def is_unchanged(self, file_path: Path) -> bool:
        """Check if file is unchanged since last scan.

        Args:
            file_path: Path to file

        Returns:
            True if file hash matches cached hash
        """
        file_str = str(file_path)
        cached_hash = self.get_hash(file_str)
        if cached_hash is None:
            return False

        current_hash = self.compute_hash(file_path)
        return current_hash == cached_hash

    def update_file(self, file_path: Path) -> tuple[bool, str]:
        """Update cache entry for a file.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (changed, hash) where changed is True if file was modified
        """
        file_str = str(file_path)
        current_hash = self.compute_hash(file_path)

        cached_hash = self.get_hash(file_str)
        changed = cached_hash != current_hash

        self.set_hash(file_str, current_hash)

        return changed, current_hash

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache = {}

    def cleanup(self, existing_files: set[str]) -> None:
        """Remove cache entries for files that no longer exist.

        Args:
            existing_files: Set of file paths that currently exist
        """
        to_remove = [path for path in self.cache if path not in existing_files]
        for path in to_remove:
            self.remove(path)

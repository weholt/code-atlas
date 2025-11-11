"""Tests for file caching system."""

from pathlib import Path

import pytest

from code_atlas.cache import FileCache


@pytest.fixture
def temp_cache(tmp_path):
    """Create temporary cache file."""
    cache_file = tmp_path / "test_cache.json"
    return FileCache(cache_file)


def test_cache_init(tmp_path):
    """Test cache initialization."""
    cache_file = tmp_path / "cache.json"
    cache = FileCache(cache_file)

    assert cache.cache_file == cache_file
    assert cache.cache == {}


def test_cache_compute_hash(temp_cache, tmp_path):
    """Test file hash computation."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def hello(): pass")

    file_hash = temp_cache.compute_hash(test_file)

    assert isinstance(file_hash, str)
    assert len(file_hash) == 64  # SHA-256 hex digest length


def test_cache_set_get_hash(temp_cache):
    """Test storing and retrieving hash."""
    temp_cache.set_hash("file.py", "abc123")

    assert temp_cache.get_hash("file.py") == "abc123"
    assert temp_cache.get_hash("missing.py") is None


def test_cache_is_unchanged(temp_cache, tmp_path):
    """Test unchanged file detection."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def hello(): pass")

    # Compute and store initial hash
    file_hash = temp_cache.compute_hash(test_file)
    temp_cache.set_hash(str(test_file), file_hash)

    # File should be unchanged
    assert temp_cache.is_unchanged(test_file) is True

    # Modify file
    test_file.write_text("def hello(): return 42")

    # File should be changed
    assert temp_cache.is_unchanged(test_file) is False


def test_cache_update_file(temp_cache, tmp_path):
    """Test update_file method."""
    test_file = tmp_path / "test.py"
    test_file.write_text("initial content")

    # First update (new file)
    changed, file_hash = temp_cache.update_file(test_file)
    assert changed is True
    assert len(file_hash) == 64

    # No change
    changed, file_hash2 = temp_cache.update_file(test_file)
    assert changed is False
    assert file_hash == file_hash2

    # Modify file
    test_file.write_text("modified content")
    changed, file_hash3 = temp_cache.update_file(test_file)
    assert changed is True
    assert file_hash != file_hash3


def test_cache_remove(temp_cache):
    """Test removing cache entry."""
    temp_cache.set_hash("file.py", "abc123")
    assert temp_cache.get_hash("file.py") == "abc123"

    temp_cache.remove("file.py")
    assert temp_cache.get_hash("file.py") is None


def test_cache_clear(temp_cache):
    """Test clearing all cache entries."""
    temp_cache.set_hash("file1.py", "abc123")
    temp_cache.set_hash("file2.py", "def456")

    temp_cache.clear()

    assert temp_cache.cache == {}


def test_cache_cleanup(temp_cache):
    """Test cleanup of stale entries."""
    temp_cache.set_hash("file1.py", "abc123")
    temp_cache.set_hash("file2.py", "def456")
    temp_cache.set_hash("file3.py", "ghi789")

    # Only file1 and file3 still exist
    existing_files = {"file1.py", "file3.py"}
    temp_cache.cleanup(existing_files)

    assert temp_cache.get_hash("file1.py") == "abc123"
    assert temp_cache.get_hash("file2.py") is None  # Removed
    assert temp_cache.get_hash("file3.py") == "ghi789"


def test_cache_persistence(tmp_path):
    """Test cache save and load."""
    cache_file = tmp_path / "persistent_cache.json"

    # Create and populate cache
    cache1 = FileCache(cache_file)
    cache1.set_hash("file1.py", "hash1")
    cache1.set_hash("file2.py", "hash2")
    cache1.save()

    # Load cache in new instance
    cache2 = FileCache(cache_file)

    assert cache2.get_hash("file1.py") == "hash1"
    assert cache2.get_hash("file2.py") == "hash2"


def test_cache_load_invalid_json(tmp_path):
    """Test loading corrupted cache file."""
    cache_file = tmp_path / "corrupt_cache.json"
    cache_file.write_text("{ invalid json")

    cache = FileCache(cache_file)

    # Should gracefully handle corruption with empty cache
    assert cache.cache == {}


def test_cache_compute_hash_missing_file(temp_cache, tmp_path):
    """Test hash computation for missing file."""
    missing_file = tmp_path / "nonexistent.py"

    file_hash = temp_cache.compute_hash(missing_file)

    assert file_hash == ""  # Empty hash for missing files

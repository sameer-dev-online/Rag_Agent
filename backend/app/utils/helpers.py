from typing import Any, Dict, List
import hashlib
import json


def generate_hash(text: str) -> str:
    """
    Generate SHA256 hash for a given text.

    Args:
        text: Input text

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(text.encode()).hexdigest()


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize metadata dictionary to ensure JSON serialization.

    Args:
        metadata: Input metadata dictionary

    Returns:
        Sanitized metadata dictionary
    """
    if not metadata:
        return {}

    sanitized = {}
    for key, value in metadata.items():
        try:
            # Test if value is JSON serializable
            json.dumps(value)
            sanitized[key] = value
        except (TypeError, ValueError):
            # Convert to string if not serializable
            sanitized[key] = str(value)

    return sanitized


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to append (default: "...")

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later dicts taking precedence.

    Args:
        *dicts: Variable number of dictionaries

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

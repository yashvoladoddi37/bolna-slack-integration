"""Utility functions for formatting data"""


def format_duration(seconds: int | None) -> str:
    """
    Convert seconds to human-readable format.

    >>> format_duration(45)
    '45s'
    >>> format_duration(150)
    '2m 30s'
    >>> format_duration(3665)
    '1h 1m 5s'
    >>> format_duration(None)
    'N/A'
    """
    if seconds is None:
        return "N/A"

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"

    minutes, secs = divmod(seconds, 60)

    if minutes < 60:
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"

    hours, mins = divmod(minutes, 60)
    parts = [f"{hours}h"]
    if mins:
        parts.append(f"{mins}m")
    if secs:
        parts.append(f"{secs}s")
    return " ".join(parts)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max_length, appending suffix if cut.

    >>> truncate_text("Hello World", 8)
    'Hello...'
    >>> truncate_text("Short", 10)
    'Short'
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix

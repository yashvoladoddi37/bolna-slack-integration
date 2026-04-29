"""Utility functions for formatting data"""

from typing import List
from app.models import TranscriptMessage


def format_duration(seconds: int) -> str:
    """
    Convert seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string (e.g., "2m 30s", "1h 15m")
    
    Examples:
        >>> format_duration(45)
        '45s'
        >>> format_duration(150)
        '2m 30s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if remaining_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_seconds == 0:
        if remaining_minutes == 0:
            return f"{hours}h"
        return f"{hours}h {remaining_minutes}m"
    
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


def format_transcript(messages: List[TranscriptMessage], max_length: int = 3000) -> str:
    """
    Format transcript messages for Slack display
    
    Args:
        messages: List of transcript messages
        max_length: Maximum length of formatted transcript
    
    Returns:
        Formatted transcript string
    
    Examples:
        >>> messages = [
        ...     TranscriptMessage(role="user", message="Hello", timestamp=datetime.now()),
        ...     TranscriptMessage(role="agent", message="Hi there!", timestamp=datetime.now())
        ... ]
        >>> transcript = format_transcript(messages)
        >>> "User: Hello" in transcript
        True
    """
    if not messages:
        return "No transcript available"
    
    lines = []
    for msg in messages:
        role = msg.role.capitalize()
        lines.append(f"{role}: {msg.message}")
    
    transcript = "\n".join(lines)
    
    # Truncate if too long
    if len(transcript) > max_length:
        truncate_at = max_length - 20  # Leave room for truncation message
        transcript = transcript[:truncate_at] + "\n...(truncated)"
    
    return transcript


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated text
    
    Examples:
        >>> truncate_text("Hello World", 8)
        'Hello...'
        >>> truncate_text("Short", 10)
        'Short'
    """
    if len(text) <= max_length:
        return text
    
    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix


def format_call_id(call_id: str, max_length: int = 12) -> str:
    """
    Format call ID for display (truncate if too long)
    
    Args:
        call_id: Full call ID
        max_length: Maximum display length
    
    Returns:
        Formatted call ID
    
    Examples:
        >>> format_call_id("abc123def456ghi789")
        'abc123def...'
    """
    if len(call_id) <= max_length:
        return call_id
    
    # Show first part and ellipsis
    return call_id[:max_length - 3] + "..."

# Made with Bob

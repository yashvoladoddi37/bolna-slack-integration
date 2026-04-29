"""Bolna API client for fetching call details"""

import httpx
import asyncio
from typing import Optional
from app.config import settings
from app.models import BolnaCallDetails, TranscriptMessage
from app.utils.logger import setup_logger, log_with_context


logger = setup_logger(__name__, settings.log_level)


class BolnaAPIError(Exception):
    """Custom exception for Bolna API errors"""
    pass


class BolnaClient:
    """Client for interacting with Bolna API"""
    
    def __init__(self):
        """Initialize Bolna API client"""
        self.base_url = settings.bolna_api_base_url.rstrip('/')
        self.api_key = settings.bolna_api_key
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay
        
        logger.info("Bolna client initialized", extra={
            "context": {"base_url": self.base_url}
        })
    
    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters
        
        Returns:
            HTTP response
        
        Raises:
            BolnaAPIError: If request fails after all retries
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)
                    
                    # Raise for 4xx and 5xx errors
                    response.raise_for_status()
                    
                    log_with_context(
                        logger, "info",
                        f"Request successful: {method} {url}",
                        attempt=attempt + 1,
                        status_code=response.status_code
                    )
                    
                    return response
                    
            except httpx.HTTPStatusError as e:
                last_exception = e
                status_code = e.response.status_code
                
                # Don't retry on 4xx errors (except 429 rate limit)
                if 400 <= status_code < 500 and status_code != 429:
                    log_with_context(
                        logger, "error",
                        f"Client error: {method} {url}",
                        status_code=status_code,
                        error=str(e)
                    )
                    raise BolnaAPIError(f"API request failed: {status_code} - {e.response.text}")
                
                # Retry on 5xx errors and 429
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    log_with_context(
                        logger, "warning",
                        f"Request failed, retrying in {delay}s",
                        attempt=attempt + 1,
                        status_code=status_code,
                        delay=delay
                    )
                    await asyncio.sleep(delay)
                else:
                    log_with_context(
                        logger, "error",
                        f"Request failed after {self.max_retries} attempts",
                        status_code=status_code,
                        error=str(e)
                    )
                    
            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    log_with_context(
                        logger, "warning",
                        f"Request error, retrying in {delay}s",
                        attempt=attempt + 1,
                        error=str(e),
                        delay=delay
                    )
                    await asyncio.sleep(delay)
                else:
                    log_with_context(
                        logger, "error",
                        f"Request failed after {self.max_retries} attempts",
                        error=str(e)
                    )
        
        # If we get here, all retries failed
        raise BolnaAPIError(f"Failed to complete request after {self.max_retries} attempts: {last_exception}")
    
    async def get_call_details(self, call_id: str) -> BolnaCallDetails:
        """
        Fetch complete call details from Bolna API
        
        Args:
            call_id: Unique call identifier
        
        Returns:
            Complete call details including transcript
        
        Raises:
            BolnaAPIError: If API request fails
        """
        url = f"{self.base_url}/call/{call_id}"
        
        log_with_context(
            logger, "info",
            "Fetching call details",
            call_id=call_id,
            url=url
        )
        
        try:
            response = await self._make_request_with_retry(
                "GET",
                url,
                headers=self._get_headers()
            )
            
            data = response.json()
            
            # Parse transcript messages
            transcript = []
            if "transcript" in data and data["transcript"]:
                for msg in data["transcript"]:
                    transcript.append(TranscriptMessage(**msg))
            
            # Create BolnaCallDetails object
            call_details = BolnaCallDetails(
                id=data["id"],
                agent_id=data["agent_id"],
                duration=data["duration"],
                status=data.get("status", "completed"),
                transcript=transcript,
                created_at=data["created_at"],
                ended_at=data["ended_at"]
            )
            
            log_with_context(
                logger, "info",
                "Call details fetched successfully",
                call_id=call_id,
                duration=call_details.duration,
                transcript_length=len(transcript)
            )
            
            return call_details
            
        except Exception as e:
            log_with_context(
                logger, "error",
                "Failed to fetch call details",
                call_id=call_id,
                error=str(e)
            )
            raise BolnaAPIError(f"Failed to fetch call details: {str(e)}")

# Made with Bob

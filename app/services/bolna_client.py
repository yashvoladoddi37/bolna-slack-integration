"""Bolna API client — fetches execution details by ID"""

import httpx
import asyncio
from app.config import settings
from app.models import BolnaExecutionPayload
from app.utils.logger import setup_logger, log_with_context


logger = setup_logger(__name__, settings.log_level)


class BolnaAPIError(Exception):
    """Raised when a Bolna API call fails"""
    pass


class BolnaClient:
    """Thin async client for the Bolna REST API"""

    def __init__(self):
        self.base_url = settings.bolna_api_base_url.rstrip("/")
        self.api_key = settings.bolna_api_key
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay

        logger.info("Bolna client initialized", extra={"context": {"base_url": self.base_url}})

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """HTTP request with exponential-backoff retries."""
        last_exc: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response

            except httpx.HTTPStatusError as e:
                last_exc = e
                status = e.response.status_code
                # Don't retry client errors (except 429 rate-limit)
                if 400 <= status < 500 and status != 429:
                    raise BolnaAPIError(
                        f"Bolna API client error {status}: {e.response.text}"
                    ) from e

            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_exc = e

            # Backoff before retrying
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                log_with_context(
                    logger, "warning",
                    f"Retrying request in {delay}s (attempt {attempt + 1}/{self.max_retries})",
                    url=url,
                    error=str(last_exc),
                )
                await asyncio.sleep(delay)

        raise BolnaAPIError(
            f"Request failed after {self.max_retries} attempts: {last_exc}"
        )

    async def get_execution(self, execution_id: str) -> BolnaExecutionPayload:
        """
        Fetch a specific call execution from the Bolna API.

        Endpoint: GET /executions/{execution_id}
        """
        url = f"{self.base_url}/executions/{execution_id}"

        log_with_context(logger, "info", "Fetching execution", execution_id=execution_id)

        try:
            response = await self._request("GET", url, headers=self._headers())
            data = response.json()
            return BolnaExecutionPayload(**data)
        except BolnaAPIError:
            raise
        except Exception as e:
            raise BolnaAPIError(f"Failed to parse execution response: {e}") from e

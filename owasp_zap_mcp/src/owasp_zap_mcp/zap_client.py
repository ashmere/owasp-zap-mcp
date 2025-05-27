"""
ZAP Client

Simplified ZAP API client using the zaproxy library, similar to the working demo.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from zapv2 import ZAPv2

logger = logging.getLogger(__name__)


class ZAPAlert:
    """Simple ZAP alert representation."""

    def __init__(self, alert_data: Dict[str, Any]):
        self.name = alert_data.get("name", "Unknown")
        self.risk = alert_data.get("risk", "Unknown")
        self.confidence = alert_data.get("confidence", "Unknown")
        self.url = alert_data.get("url", "")
        self.description = alert_data.get("description", "")
        self.solution = alert_data.get("solution", "")


class ZAPScanStatus:
    """Simple scan status representation."""

    def __init__(self, status: str, progress: int):
        self.status = status
        self.progress = progress


class ZAPClient:
    """Simplified ZAP client using zapv2 library."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.zap = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def connect(self):
        """Initialize ZAP connection."""
        try:
            # Initialize ZAP API client
            self.zap = ZAPv2(apikey=self.api_key, proxies=None)

            # Set the correct API URL
            if self.base_url.endswith("/"):
                self.base_url = self.base_url[:-1]
            self.zap._ZAPv2__base = self.base_url

            logger.info(f"ZAP client initialized with URL: {self.base_url}")

        except Exception as e:
            logger.error(f"Failed to initialize ZAP client: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if ZAP is accessible."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            version = await loop.run_in_executor(None, lambda: self.zap.core.version)
            logger.info(f"ZAP health check passed, version: {version}")
            return True
        except Exception as e:
            logger.error(f"ZAP health check failed: {e}")
            return False

    async def spider_scan(self, url: str, max_depth: int = 5) -> str:
        """Start a spider scan."""
        try:
            loop = asyncio.get_event_loop()

            # Configure spider settings
            await loop.run_in_executor(
                None, lambda: self.zap.spider.set_option_max_depth(max_depth)
            )
            await loop.run_in_executor(
                None, lambda: self.zap.spider.set_option_thread_count(10)
            )

            # Start spider scan
            scan_id = await loop.run_in_executor(
                None, lambda: self.zap.spider.scan(url)
            )
            logger.info(f"Spider scan started for {url} with ID {scan_id}")
            return scan_id

        except Exception as e:
            logger.error(f"Failed to start spider scan: {e}")
            raise

    async def active_scan(self, url: str, scan_policy: Optional[str] = None) -> str:
        """Start an active scan."""
        try:
            loop = asyncio.get_event_loop()

            # Configure active scan settings
            await loop.run_in_executor(
                None, lambda: self.zap.ascan.set_option_thread_per_host(10)
            )

            # Start active scan
            scan_id = await loop.run_in_executor(None, lambda: self.zap.ascan.scan(url))
            logger.info(f"Active scan started for {url} with ID {scan_id}")
            return scan_id

        except Exception as e:
            logger.error(f"Failed to start active scan: {e}")
            raise

    async def get_spider_status(self, scan_id: str) -> ZAPScanStatus:
        """Get spider scan status."""
        try:
            loop = asyncio.get_event_loop()
            progress = await loop.run_in_executor(
                None, lambda: self.zap.spider.status(scan_id)
            )
            progress_int = int(progress)

            if progress_int >= 100:
                status = "FINISHED"
            elif progress_int > 0:
                status = "RUNNING"
            else:
                status = "NOT_STARTED"

            return ZAPScanStatus(status, progress_int)

        except Exception as e:
            logger.error(f"Failed to get spider status: {e}")
            raise

    async def get_active_scan_status(self, scan_id: str) -> ZAPScanStatus:
        """Get active scan status."""
        try:
            loop = asyncio.get_event_loop()
            progress = await loop.run_in_executor(
                None, lambda: self.zap.ascan.status(scan_id)
            )
            progress_int = int(progress)

            if progress_int >= 100:
                status = "FINISHED"
            elif progress_int > 0:
                status = "RUNNING"
            else:
                status = "NOT_STARTED"

            return ZAPScanStatus(status, progress_int)

        except Exception as e:
            logger.error(f"Failed to get active scan status: {e}")
            raise

    async def get_alerts(self, risk_level: Optional[str] = None) -> List[ZAPAlert]:
        """Get security alerts."""
        try:
            loop = asyncio.get_event_loop()
            alerts_data = await loop.run_in_executor(
                None, lambda: self.zap.core.alerts()
            )

            alerts = []
            for alert_data in alerts_data:
                alert = ZAPAlert(alert_data)
                if risk_level is None or alert.risk == risk_level:
                    alerts.append(alert)

            return alerts

        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            raise

    async def generate_html_report(self) -> str:
        """Generate HTML report."""
        try:
            loop = asyncio.get_event_loop()
            report = await loop.run_in_executor(
                None, lambda: self.zap.core.htmlreport()
            )
            return report

        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            raise

    async def generate_json_report(self) -> Dict[str, Any]:
        """Generate JSON report."""
        try:
            alerts = await self.get_alerts()
            return {
                "alerts": [
                    {
                        "name": alert.name,
                        "risk": alert.risk,
                        "confidence": alert.confidence,
                        "url": alert.url,
                        "description": alert.description,
                        "solution": alert.solution,
                    }
                    for alert in alerts
                ],
                "total_alerts": len(alerts),
            }

        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            raise

    async def clear_session(self) -> bool:
        """Clear ZAP session."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.zap.core.new_session())
            return True

        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False

"""
ZAP Client

Simplified ZAP API client using the zaproxy library, similar to the working demo.
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from zapv2 import ZAPv2

# Get logger
logger = logging.getLogger("owasp-zap-client")


class ZAPScanStatus(Enum):
    """Enumeration for ZAP scan statuses."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ZAPAlert:
    """Represents a ZAP security alert."""

    alert_id: str
    name: str
    risk: str
    confidence: str
    url: str
    description: str
    solution: str
    reference: str
    plugin_id: str


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

        logger.debug(f"Initializing ZAP client with URL: {base_url}")
        logger.debug(f"API key configured: {'Yes' if api_key else 'No'}")
        logger.debug(f"Timeout: {timeout}s")

    async def __aenter__(self):
        """Async context manager entry."""
        logger.debug("Entering ZAP client context manager")
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        logger.debug("Exiting ZAP client context manager")
        if exc_type:
            logger.debug(
                f"Context manager exit with exception: {exc_type.__name__}: {exc_val}"
            )

    async def connect(self):
        """Initialize ZAP connection."""
        logger.info(f"Connecting to ZAP at {self.base_url}")

        try:
            # Extract host and port from base_url for zapv2 library
            parsed_url = urlparse(self.base_url)
            host = parsed_url.hostname or "localhost"
            port = parsed_url.port or 8080

            logger.debug(f"Parsed ZAP URL - Host: {host}, Port: {port}")

            # Initialize ZAP API client with the correct base URL
            self.zap = ZAPv2(
                apikey=self.api_key,
                proxies={
                    "http": f"http://{host}:{port}",
                    "https": f"http://{host}:{port}",
                },
            )

            logger.info(f"✅ ZAP client initialized successfully")
            logger.debug(f"ZAP proxy configuration: http://{host}:{port}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize ZAP client: {e}", exc_info=True)
            raise

    async def health_check(self) -> bool:
        """Check if ZAP is accessible."""
        logger.debug("Performing ZAP health check...")

        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            start_time = time.time()

            version = await loop.run_in_executor(None, lambda: self.zap.core.version)

            duration = time.time() - start_time
            logger.info(
                f"✅ ZAP health check passed - Version: {version} (took {duration:.2f}s)"
            )

            # Additional health checks in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                try:
                    # Check if ZAP is ready to scan
                    status = await loop.run_in_executor(
                        None, lambda: self.zap.core.version
                    )
                    logger.debug(f"ZAP core status check: {status}")

                    # Get basic ZAP info
                    mode = await loop.run_in_executor(None, lambda: self.zap.core.mode)
                    logger.debug(f"ZAP mode: {mode}")

                except Exception as debug_e:
                    logger.debug(
                        f"Additional health check failed (non-critical): {debug_e}"
                    )

            return True

        except Exception as e:
            logger.error(f"❌ ZAP health check failed: {e}")
            logger.debug(f"Health check error details: {type(e).__name__}: {str(e)}")
            return False

    async def spider_scan(self, url: str, max_depth: int = 5) -> str:
        """Start a spider scan."""
        logger.info(f"Starting spider scan for URL: {url}")
        logger.debug(f"Spider scan parameters - URL: {url}, Max depth: {max_depth}")

        try:
            loop = asyncio.get_event_loop()

            # Configure spider settings
            logger.debug("Configuring spider settings...")
            await loop.run_in_executor(
                None, lambda: self.zap.spider.set_option_max_depth(max_depth)
            )
            await loop.run_in_executor(
                None, lambda: self.zap.spider.set_option_thread_count(10)
            )
            logger.debug(f"Spider configured - Max depth: {max_depth}, Threads: 10")

            # Start spider scan
            logger.debug(f"Initiating spider scan for {url}...")
            start_time = time.time()

            scan_id = await loop.run_in_executor(
                None, lambda: self.zap.spider.scan(url)
            )

            duration = time.time() - start_time
            logger.info(
                f"✅ Spider scan started successfully - ID: {scan_id} (took {duration:.2f}s)"
            )
            logger.debug(f"Spider scan ID type: {type(scan_id)}, Value: {scan_id}")

            return scan_id

        except Exception as e:
            logger.error(
                f"❌ Failed to start spider scan for {url}: {e}", exc_info=True
            )
            raise

    async def active_scan(self, url: str, scan_policy: Optional[str] = None) -> str:
        """Start an active scan."""
        logger.info(f"Starting active scan for URL: {url}")
        logger.debug(
            f"Active scan parameters - URL: {url}, Policy: {scan_policy or 'default'}"
        )

        try:
            loop = asyncio.get_event_loop()

            # Configure active scan settings
            logger.debug("Configuring active scan settings...")
            await loop.run_in_executor(
                None, lambda: self.zap.ascan.set_option_thread_per_host(10)
            )
            logger.debug("Active scan threads configured: 10 per host")

            # Start active scan
            logger.debug(f"Initiating active scan for {url}...")
            start_time = time.time()

            scan_id = await loop.run_in_executor(None, lambda: self.zap.ascan.scan(url))

            duration = time.time() - start_time
            logger.info(
                f"✅ Active scan started successfully - ID: {scan_id} (took {duration:.2f}s)"
            )
            logger.debug(f"Active scan ID type: {type(scan_id)}, Value: {scan_id}")

            return scan_id

        except Exception as e:
            logger.error(
                f"❌ Failed to start active scan for {url}: {e}", exc_info=True
            )
            raise

    async def get_spider_status(self, scan_id: str) -> ZAPScanStatus:
        """Get spider scan status."""
        logger.debug(f"Checking spider scan status for ID: {scan_id}")

        try:
            loop = asyncio.get_event_loop()
            start_time = time.time()

            status = await loop.run_in_executor(
                None, lambda: self.zap.spider.status(scan_id)
            )

            duration = time.time() - start_time
            logger.debug(f"Spider status check completed in {duration:.2f}s")

            # Convert status to enum
            status_int = int(status)
            logger.debug(f"Spider scan {scan_id} status: {status_int}%")

            if status_int < 100:
                result = ZAPScanStatus.RUNNING
                logger.debug(
                    f"Spider scan {scan_id} is running ({status_int}% complete)"
                )
            else:
                result = ZAPScanStatus.COMPLETED
                logger.info(f"✅ Spider scan {scan_id} completed (100%)")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to get spider scan status for {scan_id}: {e}")
            logger.debug(f"Spider status error: {type(e).__name__}: {str(e)}")
            return ZAPScanStatus.UNKNOWN

    async def get_active_scan_status(self, scan_id: str) -> ZAPScanStatus:
        """Get active scan status."""
        logger.debug(f"Checking active scan status for ID: {scan_id}")

        try:
            loop = asyncio.get_event_loop()
            start_time = time.time()

            status = await loop.run_in_executor(
                None, lambda: self.zap.ascan.status(scan_id)
            )

            duration = time.time() - start_time
            logger.debug(f"Active scan status check completed in {duration:.2f}s")

            # Convert status to enum
            status_int = int(status)
            logger.debug(f"Active scan {scan_id} status: {status_int}%")

            if status_int < 100:
                result = ZAPScanStatus.RUNNING
                logger.debug(
                    f"Active scan {scan_id} is running ({status_int}% complete)"
                )
            else:
                result = ZAPScanStatus.COMPLETED
                logger.info(f"✅ Active scan {scan_id} completed (100%)")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to get active scan status for {scan_id}: {e}")
            logger.debug(f"Active scan status error: {type(e).__name__}: {str(e)}")
            return ZAPScanStatus.UNKNOWN

    async def get_alerts(self, risk_level: Optional[str] = None) -> List[ZAPAlert]:
        """Get alerts from ZAP."""
        logger.info(f"Retrieving alerts from ZAP (risk level: {risk_level or 'all'})")

        try:
            loop = asyncio.get_event_loop()
            start_time = time.time()

            # Get all alerts
            alerts_data = await loop.run_in_executor(
                None, lambda: self.zap.core.alerts()
            )

            duration = time.time() - start_time
            logger.debug(f"Retrieved raw alerts data in {duration:.2f}s")
            logger.debug(f"Raw alerts count: {len(alerts_data) if alerts_data else 0}")

            alerts = []
            risk_filter_applied = 0

            for alert_data in alerts_data:
                try:
                    alert = ZAPAlert(
                        alert_id=alert_data.get("id", ""),
                        name=alert_data.get("alert", ""),
                        risk=alert_data.get("risk", ""),
                        confidence=alert_data.get("confidence", ""),
                        url=alert_data.get("url", ""),
                        description=alert_data.get("description", ""),
                        solution=alert_data.get("solution", ""),
                        reference=alert_data.get("reference", ""),
                        plugin_id=alert_data.get("pluginId", ""),
                    )

                    # Filter by risk level if specified
                    if risk_level is None or alert.risk.lower() == risk_level.lower():
                        alerts.append(alert)
                    else:
                        risk_filter_applied += 1

                except Exception as alert_e:
                    logger.warning(f"Failed to parse alert data: {alert_e}")
                    logger.debug(f"Problematic alert data: {alert_data}")

            logger.info(f"✅ Retrieved {len(alerts)} alerts")

            if risk_filter_applied > 0:
                logger.debug(
                    f"Filtered out {risk_filter_applied} alerts not matching risk level '{risk_level}'"
                )

            # Log risk distribution in debug mode
            if logger.isEnabledFor(logging.DEBUG) and alerts:
                risk_counts = {}
                for alert in alerts:
                    risk_counts[alert.risk] = risk_counts.get(alert.risk, 0) + 1
                logger.debug(f"Alert risk distribution: {risk_counts}")

            return alerts

        except Exception as e:
            logger.error(f"❌ Failed to get alerts: {e}", exc_info=True)
            raise

    async def generate_html_report(self) -> str:
        """Generate HTML report."""
        logger.info("Generating HTML report from ZAP")

        try:
            loop = asyncio.get_event_loop()
            start_time = time.time()

            report = await loop.run_in_executor(
                None, lambda: self.zap.core.htmlreport()
            )

            duration = time.time() - start_time
            report_size = len(report) if report else 0

            logger.info(
                f"✅ Generated HTML report successfully ({report_size} bytes, took {duration:.2f}s)"
            )
            logger.debug(
                f"HTML report preview: {report[:200] if report else 'Empty report'}..."
            )

            return report

        except Exception as e:
            logger.error(f"❌ Failed to generate HTML report: {e}", exc_info=True)
            raise

    async def generate_json_report(self) -> str:
        """Generate JSON report."""
        logger.info("Generating JSON report from ZAP")

        try:
            loop = asyncio.get_event_loop()
            start_time = time.time()

            # Get alerts and format as JSON
            alerts_data = await loop.run_in_executor(
                None, lambda: self.zap.core.alerts()
            )

            # Create structured report
            report = {
                "scan_info": {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "zap_version": await loop.run_in_executor(
                        None, lambda: self.zap.core.version
                    ),
                },
                "alerts": alerts_data or [],
                "alert_counts": {},
            }

            # Add alert statistics
            if alerts_data:
                risk_counts = {}
                for alert in alerts_data:
                    risk = alert.get("risk", "Unknown")
                    risk_counts[risk] = risk_counts.get(risk, 0) + 1
                report["alert_counts"] = risk_counts

            json_report = json.dumps(report, indent=2, ensure_ascii=False)

            duration = time.time() - start_time
            report_size = len(json_report)

            logger.info(
                f"✅ Generated JSON report successfully ({report_size} bytes, took {duration:.2f}s)"
            )
            logger.debug(f"JSON report contains {len(alerts_data or [])} alerts")

            return json_report

        except Exception as e:
            logger.error(f"❌ Failed to generate JSON report: {e}", exc_info=True)
            raise

    async def clear_session(self) -> bool:
        """Clear ZAP session data."""
        logger.info("Clearing ZAP session data")

        try:
            loop = asyncio.get_event_loop()
            start_time = time.time()

            # Clear various ZAP data
            await loop.run_in_executor(None, lambda: self.zap.core.new_session())

            duration = time.time() - start_time
            logger.info(f"✅ ZAP session cleared successfully (took {duration:.2f}s)")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to clear ZAP session: {e}", exc_info=True)
            return False

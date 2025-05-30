# owasp_zap_mcp/config.py
import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file (don't override existing env vars)
load_dotenv(override=False)

# Get Log Level from environment variable, default to 'info'
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "info").upper()

# Map string level to logging level constant
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL_STR, logging.INFO)

# ZAP Configuration
ZAP_BASE_URL = os.getenv("ZAP_BASE_URL", "http://zap:8080")
ZAP_API_KEY = os.getenv("ZAP_API_KEY")

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "3000"))


def load_config():
    """Loads configuration settings."""
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info("Configuration loaded from environment variables")
    logger.info(f"ZAP Base URL: {ZAP_BASE_URL}")
    logger.info(f"Log Level: {LOG_LEVEL_STR}")

    return {
        "zap_base_url": ZAP_BASE_URL,
        "zap_api_key": ZAP_API_KEY,
        "server_host": SERVER_HOST,
        "server_port": SERVER_PORT,
        "log_level": LOG_LEVEL,
    }

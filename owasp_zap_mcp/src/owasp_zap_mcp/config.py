# owasp_zap_mcp/config.py
import logging
import os
import sys

from dotenv import load_dotenv

# Load environment variables from .env file (don't override existing env vars)
load_dotenv(override=False)

# Get Log Level from environment variable, default to 'INFO'
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()

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


def setup_logging():
    """Configure comprehensive logging with proper formatting and handlers."""

    # Create formatter for consistent log format
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific logger levels for important components
    logging.getLogger("owasp-zap-mcp").setLevel(LOG_LEVEL)
    logging.getLogger("owasp-zap-mcp-sse").setLevel(LOG_LEVEL)
    logging.getLogger("owasp-zap-mcp-core").setLevel(LOG_LEVEL)
    logging.getLogger("owasp-zap-tools").setLevel(LOG_LEVEL)

    # Reduce noise from external libraries unless in DEBUG mode
    if LOG_LEVEL > logging.DEBUG:
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("aiohttp").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging.getLogger("owasp-zap-mcp-config")


def load_config():
    """Loads configuration settings and sets up logging."""

    # Setup logging first
    logger = setup_logging()

    logger.info("=== OWASP ZAP MCP Configuration ===")
    logger.info(f"Log Level: {LOG_LEVEL_STR} ({LOG_LEVEL})")
    logger.info(f"ZAP Base URL: {ZAP_BASE_URL}")
    logger.info(f"ZAP API Key: {'SET' if ZAP_API_KEY else 'NOT SET'}")
    logger.info(f"Server Host: {SERVER_HOST}")
    logger.info(f"Server Port: {SERVER_PORT}")
    logger.info("=" * 40)

    # Debug logging for environment variables
    if LOG_LEVEL <= logging.DEBUG:
        logger.debug("Environment Variables Debug:")
        env_vars = [
            "LOG_LEVEL",
            "ZAP_BASE_URL",
            "ZAP_API_KEY",
            "SERVER_HOST",
            "SERVER_PORT",
            "ALLOWED_ORIGINS",
            "MCP_ALLOW_CREDENTIALS",
            "DOCKER_DEFAULT_PLATFORM",
        ]
        for var in env_vars:
            value = os.getenv(var, "NOT SET")
            # Hide sensitive values
            if "KEY" in var and value != "NOT SET":
                value = "***HIDDEN***"
            logger.debug(f"  {var}: {value}")

    # Validate configuration
    warnings = []

    if not ZAP_BASE_URL.startswith(("http://", "https://")):
        warnings.append(
            f"ZAP_BASE_URL should start with http:// or https://, got: {ZAP_BASE_URL}"
        )

    if SERVER_PORT < 1024 and os.geteuid != 0:
        warnings.append(f"Port {SERVER_PORT} requires root privileges on some systems")

    for warning in warnings:
        logger.warning(f"Configuration Warning: {warning}")

    return {
        "zap_base_url": ZAP_BASE_URL,
        "zap_api_key": ZAP_API_KEY,
        "server_host": SERVER_HOST,
        "server_port": SERVER_PORT,
        "log_level": LOG_LEVEL,
        "log_level_str": LOG_LEVEL_STR,
    }

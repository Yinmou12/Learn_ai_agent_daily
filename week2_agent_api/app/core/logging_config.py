import logging
import sys

from app.config import load_settings


def setup_logging() -> None:
    """
    配置应用日志

    logging.basicConfig 只需要在应用启动时配置一次
    """

    settings = load_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

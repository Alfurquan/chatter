import os


LOGGING_CONFIG = {
    "DEFAULT_LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
    "DEFAULT_LOG_FORMAT": os.environ.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
}
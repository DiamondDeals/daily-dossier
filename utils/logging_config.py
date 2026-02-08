"""
Logging configuration for PersonalizedReddit application
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
import structlog
from typing import Dict, Any

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """
    Setup structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure standard library logging
    log_file = log_path / f"personalized_reddit_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)  # Less verbose for console
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Suppress verbose third-party logs
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("prawcore").setLevel(logging.INFO)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)

def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)

class LogCapture:
    """Context manager to capture logs for debugging"""
    
    def __init__(self, logger_name: str = None, level: int = logging.INFO):
        self.logger_name = logger_name or 'root'
        self.level = level
        self.logs = []
        self.handler = None
        
    def __enter__(self):
        self.handler = logging.Handler()
        self.handler.setLevel(self.level)
        self.handler.emit = lambda record: self.logs.append(self.handler.format(record))
        
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(self.handler)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
    
    def get_logs(self) -> list:
        """Get captured logs"""
        return self.logs.copy()

def log_performance(func):
    """Decorator to log function performance"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(
                f"Function {func.__name__} completed",
                duration_seconds=round(duration, 3),
                function=func.__name__,
                module=func.__module__
            )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(
                f"Function {func.__name__} failed",
                duration_seconds=round(duration, 3),
                function=func.__name__,
                module=func.__module__,
                error=str(e)
            )
            raise
    
    return wrapper
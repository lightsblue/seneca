"""Logging configuration manager for the Latin Translator project."""

import logging
from typing import Optional

class LoggingManager:
    """Manages logging configuration across the Latin Translator project.
    
    This class encapsulates all logging-related functionality, providing a clean interface
    for configuring and managing loggers across the project. It handles both general logging
    setup and specific configurations for different components (e.g., OpenAI, notebooks).
    
    Example:
        >>> logging_manager = LoggingManager()
        >>> logging_manager.configure_base_logging()
        >>> logger = logging_manager.get_notebook_logger('my_notebook')
    """
    
    def __init__(self):
        """Initialize the LoggingManager with default settings."""
        self._base_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self._configured = False
    
    def configure_base_logging(self, level: int = logging.INFO) -> None:
        """Configure the base logging settings for the project.
        
        Args:
            level: The base logging level to use. Defaults to INFO.
        """
        if not self._configured:
            # Removed basicConfig to use global configuration
            # Set third-party loggers to WARNING to reduce noise
            logging.getLogger('httpx').setLevel(logging.WARNING)
            self._configured = True
    
    def get_notebook_logger(self, name: str, level: Optional[int] = None) -> logging.Logger:
        """Get a logger configured for use in notebooks.
        
        Args:
            name: The name for the logger
            level: Optional specific level for this logger. If None, uses the root logger's level.
        
        Returns:
            A configured logger instance
        """
        if not self._configured:
            self.configure_base_logging()
            
        logger = logging.getLogger(name)
        if level is not None:
            logger.setLevel(level)
        return logger
    
    def configure_openai_logging(self, enable: bool = False) -> None:
        """Configure detailed logging for OpenAI-related operations.
        
        Args:
            enable: Whether to enable detailed OpenAI logging
        """
        if not self._configured:
            self.configure_base_logging()
            
        http_logger = logging.getLogger('latin_translator.service.orchestrator.http')
        orchestrator_logger = logging.getLogger('latin_translator.service.orchestrator')
        
        level = logging.DEBUG if enable else logging.WARNING
        http_logger.setLevel(level)
        orchestrator_logger.setLevel(level if enable else logging.INFO)
        
        status = "enabled" if enable else "disabled"
        logging.getLogger('translate_letter').info(f"OpenAI debug logging {status}")
    
    @property
    def is_configured(self) -> bool:
        """Check if base logging has been configured.
        
        Returns:
            bool: True if base logging has been configured, False otherwise.
        """
        return self._configured 
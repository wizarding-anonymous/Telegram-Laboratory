import os
import sys
import structlog

def configure_logger(service_name: str = "ServiceDiscovery"):
    """
    Configures the structlog logger.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
            foreign_preprocessors=[
               structlog.stdlib.ProcessorFormatter.remove_processors_attribute,
            ]
    )

    handler = structlog.stdlib.ProcessorFormatter.wrap_for_formatter(formatter)

    logger = structlog.get_logger(service_name)

    if service_name == "ServiceDiscovery":
       logger.info(f"LoggingClient initialized for service: {service_name}")
    return logger


logger = configure_logger()
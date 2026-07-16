import structlog
import logging

def init_logger(
    name: str, 
    dir: str, 
    retention_days: int=30,
    ):
    structlog.configure(
            processors = [
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
                structlog.dev.ConsoleRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False
    )
    return get_logger(name)

def get_logger(name: str):
    return structlog.get_logger()

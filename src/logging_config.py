import logging
import os
from pythonjsonlogger.json import JsonFormatter

LOG_DIR = os.path.expanduser(os.getenv("LOG_DIR", "~/sre-monitoring-suite/logs"))
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", 7))


def setup_logging(check_name: str = "sre-monitor"):
    """
    Configura logging JSON estructurado para todos los scripts.
    
    Args:
        check_name: Nombre del script/componente que llama al logger.
                    Aparecerá en cada línea de log como 'component'.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(message)s %(component)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
        },
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    class ComponentFilter(logging.Filter):
        def filter(self, record):
            record.component = check_name
            return True

    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, f"{check_name}.log")),
    ]

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.addFilter(ComponentFilter())
        root_logger.addHandler(handler)

    logging.info("Logger initialized", extra={"component": check_name})
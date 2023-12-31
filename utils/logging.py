import logging
import logging.config

default_config = {
    "version": 1,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s - %(levelname)-8s%(name)-10s:  %(reset)s %(white)s%(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
    },
    "root": {
        "handlers": ["console"],
    },
}

# overwriting defaults
colors = {"DEBUG": "cyan"}

logging.config.dictConfig(default_config)


# have this as a simple wrapper to ensure the updated config is used
def get_logger(
    name: str, log_level: int = logging.DEBUG, propagate: bool = False
) -> logging.Logger:
    logger = logging.getLogger(name)
    root_logger = logging.getLogger()

    hdl = root_logger.handlers[0]
    hdl.formatter.log_colors.update(colors)

    logger.addHandler(hdl)
    logger.setLevel(log_level)

    # do not propergate messages to root logger -> just use the derived one
    logger.propagate = propagate

    return logger


if __name__ == "__main__":
    test_logger = get_logger("test")
    test_logger.setLevel(logging.DEBUG)
    test_logger.debug("DEBUG test")
    test_logger.info("INFO test")
    test_logger.warning("WARNING test")
    test_logger.error("ERROR test")
    test_logger.critical("CRITICAL test")

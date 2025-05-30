import logging

class Logger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("RedSentrix")

    def log(self, message, level="info"):
        level = level.lower()
        if level == "info":
            self.logger.info(message)
        elif level in ("warn", "warning"):
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.debug(message)


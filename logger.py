import logging
from datetime import datetime
from pathlib import Path
import sys


class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf) -> None:
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def setup_logger(logger_path=Path('F:\ssl_network')) -> None:
    file_name = "logs_" + str(datetime.today().date()) + "_" + str(datetime.today().time().strftime('%H_%M')) + ".log"
    logging.basicConfig(filename=(logger_path / file_name), level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.captureWarnings(True)
    logging.debug = sys.stdout
    sys.stdout = StreamToLogger(logging.getLogger('stdout'), logging.INFO)
    sys.stderr = StreamToLogger(logging.getLogger('stderr'), logging.ERROR)

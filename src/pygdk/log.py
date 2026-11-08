import logging as _logging
from enum import Enum as _Enum

logger = _logging.getLogger("pygdk")

formatter = _logging.Formatter("[%(name)s] [%(levelname)s] [%(asctime)s]: %(message)s")

handler = _logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
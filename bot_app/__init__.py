import logging

from .app import dp
from . import common, create_cake, registration


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

import os
import logging
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}.log"
LOG_DIR = "logs"
log_path = os.path.join(LOG_DIR, LOG_FILE)

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="[ %{asctime}s ] %{name}s - %{levelname}s : %{message}s"
)
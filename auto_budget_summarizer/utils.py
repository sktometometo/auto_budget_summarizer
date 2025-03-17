import csv
import datetime
import logging
import os
import time
from typing import List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


def get_default_download_folder() -> Optional[str]:
    """Get the default download folder."""
    if os.name == "nt":  # Windows
        import winreg

        try:
            key_path = (
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                download_folder, _ = winreg.QueryValueEx(
                    key, "{374DE290-123F-4565-9164-39C4925E467B}"
                )
                return download_folder
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    elif os.name == "posix":  # Linux
        return os.path.expanduser("~/Downloads")
    else:
        return None


def get_latest_csv_file(download_folder: str) -> Optional[str]:
    """Get the latest CSV file in the download folder."""
    csv_files = [
        f
        for f in os.listdir(download_folder)
        if f.endswith(".csv") and os.path.isfile(os.path.join(download_folder, f))
    ]
    if not csv_files:
        return None
    latest_file = max(
        csv_files, key=lambda f: os.path.getctime(os.path.join(download_folder, f))
    )
    return os.path.join(download_folder, latest_file)

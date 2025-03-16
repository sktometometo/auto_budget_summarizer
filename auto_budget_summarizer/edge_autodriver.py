import logging
import os
import tempfile
import urllib
import zipfile
from math import e
from typing import Optional, Tuple

import win32api

logger = logging.getLogger(__name__)


def get_edge_version() -> Optional[str]:
    """Get the path to the Edge binary."""
    edge_path = os.path.join(
        os.environ["SystemDrive"]
        + "\\Program Files (x86)\\Microsoft\\Edge\\Application",
        "msedge.exe",
    )
    file_version = win32api.GetFileVersionInfo(edge_path, "\\")
    ms, ls = file_version["FileVersionMS"], file_version["FileVersionLS"]
    version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
    major_version = ms >> 16
    minor_version = ms & 0xFFFF
    build_version = ls >> 16
    revision_version = ls & 0xFFFF
    version = f"{major_version}.{minor_version}.{build_version}.{revision_version}"
    return version


def download_edge_webdriver(full_version: str, directory: str) -> None:
    """Download the Edge WebDriver for the given version."""
    zip_filepath = os.path.join(tempfile.gettempdir(), "edgedriver_win64.zip")
    extract_dir = os.path.join(tempfile.gettempdir(), "edgedriver")
    url = f"https://msedgedriver.azureedge.net/{full_version}/edgedriver_win64.zip"
    logger.info(f"Downloading Edge WebDriver from {url}")
    # Download the WebDriver from the URL
    urllib.request.urlretrieve(url, zip_filepath)
    # Unzip the WebDriver
    with zipfile.ZipFile(zip_filepath, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    # Move the WebDriver to the specified directory
    webdriver_path = os.path.join(extract_dir, "msedgedriver.exe")
    os.makedirs(directory, exist_ok=True)
    target_path = os.path.join(directory, "msedgedriver.exe")
    os.rename(webdriver_path, target_path)

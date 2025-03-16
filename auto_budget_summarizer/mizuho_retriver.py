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


def get_latest_csv_file(download_folder: str):
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


def download_csv_data(cust_no: str, password: str):
    if os.name == "nt":  # Windows
        driver = webdriver.Edge()
    else:  # Linux
        driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 10)
    driver.get("https://web.ib.mizuhobank.co.jp/servlet/LOGBNK0000000B.do")
    # driver.find_element(By.NAME, "txbCustNo").send_keys(cust_no)
    element = wait.until(EC.presence_of_element_located((By.NAME, "txbCustNo")))
    element.send_keys(cust_no)
    driver.find_element(By.CLASS_NAME, "btn-primary").click()
    # driver.find_element(By.NAME, "PASSWD_LoginPwdInput").send_keys(password)
    element = wait.until(
        EC.presence_of_element_located((By.NAME, "PASSWD_LoginPwdInput"))
    )
    element.send_keys(password)
    driver.find_element(By.CLASS_NAME, "btn-primary").click()
    #
    deadline = time.time() + 5.0
    while time.time() < deadline:
        if driver.page_source.find("重要なお知らせ") != -1:
            driver.find_element(By.CLASS_NAME, "btn-primary").click()
            break
        time.sleep(0.1)
    ## Opened main page
    logger.warning("Opened main page")

    time.sleep(5.0)
    found = False
    for elem in driver.find_elements(By.CLASS_NAME, "lnk-text"):
        if (
            elem.text == "もっと見る"
            and elem.get_property("href").find("200003B") != -1
        ):
            found = True
            elem.click()
            break
    if not found:
        logger.error("Failed to find the see details link")
        return None
    ##
    time.sleep(5.0)
    found = False
    for elem in driver.find_elements(By.CLASS_NAME, "btn-mini"):
        if elem.text == "CSVダウンロード":
            found = True
            elem.click()
            break
    if not found:
        logger.error("Failed to find the csv downloading link")
        return None
    ##
    time.sleep(5.0)
    driver.quit()
    return get_latest_csv_file(get_default_download_folder())


def load_csv_data(file_path: str) -> Tuple[List[str], List[Tuple[str, int, str]]]:
    with open(file_path, "r", encoding="shift-jis") as f:
        reader = csv.reader(f)
        data = [row for row in reader]

    metadata = data[: data.index([])]
    #
    header = data[data.index([]) + 1]
    data = data[data.index([]) + 2 :]
    log = data[: data.index([])]

    def parse_log_entry(entry):
        transactionid, raw_date, money_out, money_in, balance, description = entry
        money = -int(money_out) if money_out != "" else int(money_in)
        return raw_date, money, description

    return metadata, [parse_log_entry(entry) for entry in log]


def extract_log(
    start_date: str, end_date: str, log_entries: List[Tuple[str, int, str]]
) -> List[Tuple[str, int, str]]:
    start_date = datetime.datetime.strptime(start_date, "%Y.%m.%d")
    end_date = datetime.datetime.strptime(end_date, "%Y.%m.%d")
    return [
        entry
        for entry in log_entries
        if start_date <= datetime.datetime.strptime(entry[0], "%Y.%m.%d") <= end_date
    ]

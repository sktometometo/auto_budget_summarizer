import csv
import datetime
import logging
import os
import time
from typing import List, Optional, Tuple

import google.generativeai as genai
import undetected_chromedriver as uc
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

from .utils import get_default_download_folder, get_latest_csv_file


def download_vpass_log(
    vpass_id: str, pw: str, target: Optional[str] = None
) -> Optional[str]:
    driver = uc.Chrome()
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.smbc-card.com/mem/index.jsp")

    # Login
    wait.until(EC.presence_of_element_located((By.ID, "id_input"))).send_keys(vpass_id)
    wait.until(EC.presence_of_element_located((By.ID, "pw_input"))).send_keys(pw)
    driver.find_element(By.CLASS_NAME, "btnNormal").click()
    wait.until(
        EC.presence_of_element_located((By.NAME, "vp-view-WebApiId_U000100_9"))
    ).click()
    if target is None:
        wait.until(
            EC.presence_of_element_located(
                (By.NAME, "vp-view-VC0501002_RS0001_U050100_btn-03")
            )
        ).click()
    else:
        wait.until(
            EC.presence_of_element_located(
                (By.NAME, "vp-view-VC0501002_RS0001_U050100_btn-03")
            )
        )
        driver.get(
            f"https://www.smbc-card.com/memx/web_meisai/top/index.html?p01={target}"
        )
        wait.until(
            EC.presence_of_element_located(
                (By.NAME, "vp-view-VC0502-003_RS0001_U051111_3")
            )
        ).click()
    time.sleep(3)
    driver.quit()
    return get_latest_csv_file(get_default_download_folder())


def load_vpass_csv_data(
    file_path: str,
) -> List[Tuple[datetime.datetime, str, int, str]]:
    with open(file_path, "r", encoding="shift-jis") as f:
        reader = csv.reader(f)
        data = [row for row in reader]

    ans = []

    if len(data[0]) == 3:
        for row in data:
            try:
                date = datetime.datetime.strptime(row[0], "%Y/%m/%d")
            except ValueError:
                continue
            content = row[1]
            price = int(row[2].replace(",", ""))
            appendix = row[6]
            ans.append((date, content, price, appendix))
    else:
        for row in data:
            try:
                date = datetime.datetime.strptime(row[0], "%Y/%m/%d")
            except ValueError:
                continue
            content = row[1]
            price = int(row[6].replace(",", ""))
            appendix = ""
            ans.append((date, content, price, appendix))
    ans = sorted(ans, key=lambda x: x[0])
    return ans


def add_category_to_vpass_data(
    vpass_data: List[Tuple[datetime.datetime, str, int, str]],
    categories: List[str] = [
        "00食料品・日用品",
        "01外食費",
        "02インフラ代",
        "03交通費",
        "04医療費",
        "05娯楽費",
        "06交際費",
        "99その他",
    ],
    examples: List[Tuple[str, str]] = [],
    GOOGLE_API_KEY: Optional[str] = None,
) -> List[Tuple[datetime.datetime, str, int, str, str]]:
    if GOOGLE_API_KEY is None:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = "クレジットカードの明細をカテゴリ分けします。以下の明細をカテゴリ分けしてください。\n"
    prompt += "カテゴリ一覧:\n"
    for category in categories:
        prompt += f"- {category}\n"
    prompt += "\n"
    prompt += "カテゴリ分け例 (明細: カテゴリ):\n"
    for example in examples:
        prompt += f"- {example[0]}: {example[1]}\n"
    prompt += "\n"
    prompt += "カテゴリ分け対象の明細一覧:\n"
    for i, data in enumerate(vpass_data):
        prompt += f"{i}: {data[1]}"
    prompt += "\n"
    prompt += "カテゴリ分けの結果を以下の形式で出力してください。\n"
    prompt += "```\n"
    prompt += "- id: <明細番号>\n"
    prompt += "  name: <明細>\n"
    prompt += "  category: <カテゴリ>\n"
    prompt += "- id: <明細番号>\n"
    prompt += "  name: <明細>\n"
    prompt += "  category: <カテゴリ>\n"
    prompt += "...\n"
    prompt += "```\n"
    prompt += "\n"
    prompt += "出力結果\n"
    response = model.generate_content(prompt)

    try:
        data_categories = yaml.load(
            response.text.replace("```", ""), Loader=yaml.SafeLoader
        )
    except Exception as e:
        logger.error(f"Failed to parse the response: {response.text}")
        logger.error(e)
        return

    ans = []
    for data_category in data_categories:
        data_id = int(data_category["id"])
        date = vpass_data[data_id][0]
        content = vpass_data[data_id][1]
        price = vpass_data[data_id][2]
        appendix = vpass_data[data_id][3]
        category = data_category["category"]
        ans.append((date, content, price, appendix, category))
    return ans

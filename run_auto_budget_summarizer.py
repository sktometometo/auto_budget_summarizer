import argparse
import logging
import datetime
import yaml

from auto_budget_summarizer.budget_visualizer import *
from auto_budget_summarizer.mizuho_retriver import *
from auto_budget_summarizer.vpass_retriever import (
    add_category_to_vpass_data,
    download_vpass_log,
    load_vpass_csv_data,
)

logger = logging.getLogger(__name__)


def analyze_mizuho_balance(
    customer_id: str,
    password: str,
    start_date: str,
    end_date: str,
    filename: str,
    headless: bool = False,
):
    filepath = download_mizuho_log(customer_id, password, headless=headless)
    logger.debug("Downloaded the csv file to {}".format(filepath))
    if filepath is None:
        logging.error("Failed to download the csv file")
        return
    _, mizuho_log = load_mizuho_csv_data(filepath)
    logger.debug("Raw data: {}".format(mizuho_log))
    mizuho_log = extract_mizuho_log(start_date, end_date, mizuho_log)
    plot_balance(
        mizuho_log,
        title="Mizuho Bank Account Balance from {} to {}".format(start_date, end_date),
        filename=filename,
    )
    logger.info(
        "Generated the balance plot for Mizuho bank account to {}".format(filename)
    )


def analyze_vpass_usage(
    vpass_id: str,
    vpass_password: str,
    vpass_target: str,
    google_api_key: str,
    filename: str,
    headless: bool = False,
):
    filepath = download_vpass_log(
        vpass_id, vpass_password, vpass_target, headless=headless
    )
    if filepath is None:
        logging.error("Failed to download the csv file")
        return
    logger.debug("Downloaded the csv file to {}".format(filepath))
    if filepath is None:
        logging.error("Failed to download the csv file")
        return
    vpass_log = load_vpass_csv_data(filepath)
    vpass_log_with_category = add_category_to_vpass_data(
        vpass_log, GOOGLE_API_KEY=google_api_key
    )
    plot_credit_usage(
        vpass_log_with_category,
        filename=filename,
    )
    logger.info("Generated the credit usage plot for Vpass to {}".format(filename))


def main():
    parser = argparse.ArgumentParser(description="Visualize Mizuho bank account data.")
    parser.add_argument("config", help="Path to the config file.")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    for entry in config:
        if entry["type"] == "mizuho":
            start_date = entry.get("start_date")
            if start_date is None:
                start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime(
                    "%Y.%m.%d"
                )
            end_date = entry.get("end_date")
            if end_date is None:
                end_date = datetime.datetime.now().strftime("%Y.%m.%d") 
            analyze_mizuho_balance(
                entry["customer_id"],
                entry["password"],
                entry["start_date"],
                entry["end_date"],
                entry["filename"],
                headless=args.headless,
            )
        elif entry["type"] == "vpass":
            vpass_target = entry.get("vpass_target")
            if vpass_target is None:
                vpass_target = datetime.datetime.now().strftime("%Y%m")
            analyze_vpass_usage(
                entry["vpass_id"],
                entry["vpass_password"],
                entry["vpass_target"],
                entry["google_api_key"],
                entry["filename"],
                headless=args.headless,
            )
        else:
            logging.error("Unknown type: {}".format(entry["type"]))

    logger.info("Done.")


if __name__ == "__main__":
    main()

from auto_budget_summarizer.budget_visualizer import *
from auto_budget_summarizer.mizuho_retriver import *

filepath = "D:\\Home\\Downloads\\2025031601691938415578720.csv"
log = load_csv_data(filepath)
log = extract_log("2025.02.11", "2025.03.10", log[1])

plot_balance(log)

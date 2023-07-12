import subprocess
import threading
import argparse
from datetime import datetime, timedelta
import calendar

def split_month(year, month):
    _, num_days = calendar.monthrange(year, month)
    days_per_period = num_days // 3

    dates = []
    for i in range(3):
        start_day = i * days_per_period + 1
        if i == 2:  # last period takes remaining days
            end_day = num_days
        else:
            end_day = (i + 1) * days_per_period

        start_date = datetime(year, month, start_day)
        end_date = datetime(year, month, end_day)
        
        dates.append((start_date.strftime('%d/%m/%Y'), end_date.strftime('%d/%m/%Y')))

    return dates



def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offset', type=str)
    args = parser.parse_args()
    offset = int(args.offset)
    commands = []
    threads = []
#---------------設計多執行緒下指令---------------#
    for off in [offset, offset+10000]:
        commands.append(['scrapy', 'crawl', 'jlr_judgement_info', '-a', f'offset={off}'])

# ---------------啟動多執行緒---------------#
    print(commands)
    for command in commands:
        t = threading.Thread(target=run_command, args=(command,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
#---------------從指令設定start_year和end_year---------------#
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--year', default="2019", type=str, help='Searching Year.')
#     parser.add_argument('--month', default="08", type=str, help='Searching Month.')
#     args = parser.parse_args()
#     year = int(args.year)
#     month = int(args.month)
#     commands = []
#     threads = []
# #---------------設計多執行緒下指令---------------#
#     for start_day, end_day in split_month(year, month):
#         commands.append(['scrapy', 'crawl', 'jlr_judgement_link', '-a', f'start_date={start_day}', '-a', f'end_date={end_day}'])

# # ---------------啟動多執行緒---------------#
#     print(commands)
#     for command in commands:
#         t = threading.Thread(target=run_command, args=(command,))
#         threads.append(t)
#         t.start()
#     for t in threads:
#         t.join()
        
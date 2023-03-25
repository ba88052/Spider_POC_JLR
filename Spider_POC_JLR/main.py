import subprocess
import threading
import argparse
def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
#---------------從指令設定start_year和end_year---------------#
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_year', default="2023", type=str, help='Searching Start Year.')
    parser.add_argument('--end_year', default="2023", type=str, help='Searching End Year.')
    args = parser.parse_args()
    start_year = int(args.start_year)
    end_year = int(args.end_year)
    commands = []
    threads = []
#---------------設計多執行緒下指令---------------#
    if start_year == end_year:
        commands.append(['scrapy', 'crawl', 'jlr_judgement_link', '-a', f'start_date=01/01/{start_year}', '-a', f'end_date=01/06/{end_year}'])
        commands.append(['scrapy', 'crawl', 'jlr_judgement_link', '-a', f'start_date=01/06/{start_year}', '-a', f'end_date=01/12/{end_year}'])
    else:
        step = int((end_year - start_year) /2)
        for year in range(start_year, end_year+1, step):
            commands.append(['scrapy', 'crawl', 'jlr_judgement_link', '-a', f'start_date=01/01/{year}', '-a', f'end_date=03/01/{year+step-1}'])
#---------------啟動多執行緒---------------#
    for command in commands:
        t = threading.Thread(target=run_command, args=(command,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
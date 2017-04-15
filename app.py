import argparse
import json
import requests
from bs4 import BeautifulSoup


class FootballScraper:
    def __init__(self, team_url):
        self.team_url = team_url
        self.data = []

    @staticmethod
    def get_source(url):
        page = requests.get(url)
        source = BeautifulSoup(page.content, "html.parser")
        return source

    @staticmethod
    def check_result(source):
        source = source.split('/')[-1]
        results = {
            'w.gif': 'win',
            'd.gif': 'draw',
            'l.gif': 'lose',
        }
        try:
            return results[source]
        except KeyError:
            return 'cancelled'

    def count_pages(self):
        source = self.get_source(self.team_url)
        last_page_number = source.find_all('a', class_='stat_ajax_click')[1].get(
            'href').split('/')[-1]
        all_pages = ''.join([x for x in last_page_number if x.isdigit()])
        return int(all_pages)

    def make_urls(self):
        base_url = self.team_url + '?Ajax=1&statTR-Page='
        return [base_url + str(page) for page in range(0, self.count_pages() + 1)]

    def get_data(self, url):
        while True:
            try:
                source = self.get_source(url)
                data_table = source.find('table', class_='stat')
                for row in data_table.find_all('tr'):
                    details = row.find_all('td')
                    match = {
                        'date': details[0].text,
                        'home_team': details[2].text,
                        'score': details[3].text,
                        'away_team': details[4].text,
                        'result': self.check_result(row.find('img').get('src'))
                    }
                    self.data.append(match)
                break
            except AttributeError:
                break

    def save_data(self):
        report_name = self.team_url.split('/')[-3] + '.json'
        with open(report_name, "a") as report:
            json.dump(self.data, report)

    def run(self):
        if self.team_url.endswith('/results/'):
            for url in self.make_urls():
                self.get_data(url)
            self.save_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--team")
    args = parser.parse_args()
    FootballScraper(args.team).run()

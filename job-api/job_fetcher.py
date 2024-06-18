import requests
import csv
import os
from dotenv import load_dotenv
from pathlib import Path

class JobFetcher:
    def __init__(self, csv_path = None):
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.password = os.getenv("PASSWORD")
        self.api_path = os.getenv("API_PATH")
        self.base_url = "https://api.softgarden.io"
        self.job_or_trainee_mappings = {
            "2": "Auszubildendenstelle",
            "6": "Festanstellung",
            "fe9a669ca70d49a88d972a860742b379": "Aushilfe"
        }
        self.job_or_trainee_default = "6"
        self.job_or_trainee_category_name = "Stellentyp"
        self.full_or_parttime_mappings = {
            "799eb9d2c0bc4e7490fde05f847b331a": "Teilzeitstelle",
            "137caf67764c4b63b0272895af1704b0": "Vollzeitstelle",
            "87af1987840d4442b87f2e0ee3344a1f": "Voll- oder Teilzeit"
        }
        self.full_or_parttime_default = "137caf67764c4b63b0272895af1704b0"
        self.full_or_parttime_name = "Arbeitszeit"
        self.jobexperience_mappings = {
            "1b4f51fe628c4119a2d7a581557d0944": "mit Berufserfahrung"
        }

        if not all([self.client_id, self.password, self.api_path]):
            raise ValueError('Check your .env variables!')

        if csv_path is None:
            p = Path(__file__).parent.resolve()
            csv_path = p / "jobs.csv"
        self.csv_path = csv_path

    def fetch_jobs(self):
        joblist_url = self.base_url + str(self.api_path)
        try:
            response = requests.get(joblist_url, auth=(self.client_id, self.password))
            response.encoding = 'utf-8'
            jobs = response.json()["results"]
            self.process_jobs(jobs)
        except Exception as e:
            print(f"API request failed: {e}")
            exit(1)

    def process_jobs(self, jobs):
        csv_keys = list(jobs[0].keys()) + [self.job_or_trainee_category_name, self.full_or_parttime_name]
        try:
            with open(self.csv_path, "w", encoding='utf8') as file:
                dw = csv.DictWriter(file, csv_keys, delimiter=";")
                dw.writeheader()
                for row in jobs:
                    row[self.job_or_trainee_category_name] = self.map_values(row, self.job_or_trainee_mappings, self.job_or_trainee_default, self.job_or_trainee_category_name)
                    row[self.full_or_parttime_name] = self.map_values(row, self.full_or_parttime_mappings, self.full_or_parttime_default, self.full_or_parttime_name)
                    dw.writerow(row)
        except Exception as e:
            print(f"Writing CSV failed: {e}")
            exit(1)

    def map_values(self, row, mapping_dict, default_value, field_name):
        try:
            values = [mapping_dict[str(val)] for val in row[field_name] if str(val) in mapping_dict]
            return ", ".join(values)
        except KeyError:
            return mapping_dict[default_value]

# Example usage:
if __name__ == '__main__':
    job_fetcher = JobFetcher()
    job_fetcher.fetch_jobs()

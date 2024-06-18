import requests
import csv
import os
from dotenv import load_dotenv

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
            csv_path = "jobs.csv"
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


# # -*- coding: utf-8 -*-
# import requests
# import csv
# import os
# from dotenv import load_dotenv

# load_dotenv()
# clientId = os.getenv("CLIENT_ID", False)
# password = os.getenv("PASSWORD", False)
# api_path = os.getenv("API_PATH", False)

# if (any(x is False for x in [clientId, password, api_path])):
#     print('Check your .env variables!')
#     exit(1)

# baseUrl = "https://api.softgarden.io"
# joblistUrl = baseUrl + str(api_path)

# jobOrTraineeFieldName = "employmentTypes"
# jobOrTraineeMappings = {
#     "2": "Auszubildendenstelle",
#     "6": "Festanstellung",
#     "fe9a669ca70d49a88d972a860742b379": "Aushilfe"
# }
# jobOrTraineeMappingsDefault = "6"
# jobOrTraineeCategoryNameForWebsite = "Stellentyp"

# fullOrParttimeFieldname = 'workTimes'
# fullOrParttimeMappings = {
#         "799eb9d2c0bc4e7490fde05f847b331a": "Teilzeitstelle",
#         "137caf67764c4b63b0272895af1704b0": "Vollzeitstelle",
#         "87af1987840d4442b87f2e0ee3344a1f": "Voll- oder Teilzeit"
# }
# fullOrParttimeDefault = "137caf67764c4b63b0272895af1704b0"
# fullOrParttimeNameForWebsite = "Arbeitszeit"

# # Fetch list of jobs
# try:
#     response = requests.get(joblistUrl, auth=(clientId, password))
#     response.encoding = 'utf-8'
#     jsonResult = response.json()["results"]
#     # Adding "Stellentyp" as new key to the results
#     csvKeys = list (jsonResult[0].keys())
#     csvKeys.append(jobOrTraineeCategoryNameForWebsite)
#     csvKeys.append(fullOrParttimeNameForWebsite)
# except:
#     print("API request failed.")
#     exit(1)


# try:
#     with open("./jobs.csv", "w", encoding='utf8') as filePointer:
#         dw = csv.DictWriter(filePointer, csvKeys, delimiter = ";")
#         dw.writeheader()
#         for row in jsonResult:
#             # Adding the translated job type to the resultset ...
#             try:
#                 collectedEmploymentTypes = [
#                     jobOrTraineeMappings[str(val)]
#                     for val in row[jobOrTraineeFieldName]
#                     if str(val) in jobOrTraineeMappings 
#                 ]
#             except:
#                 #print(f"Unknown employment type: {row[jobOrTraineeFieldName]} | using default {jobOrTraineeMappings[jobOrTraineeMappingsDefault]}")
#                 # Attention: f-Strings are not available, due to Python version being: 3 < Server < 3.6
#                 collectedEmploymentTypes = [ jobOrTraineeMappings[jobOrTraineeMappingsDefault] ]
#             row[jobOrTraineeCategoryNameForWebsite] = ", ".join(collectedEmploymentTypes)
            
#             try:
#                 collectedWorkingTimes = [
#                     fullOrParttimeMappings[str(val)]
#                     for val in row[fullOrParttimeFieldname]
#                     if str(val) in fullOrParttimeMappings 
#                 ]
#             except:
#                 # print(f"Unknown employment type: {row[fullOrParttimeFieldname]} | using default {fullOrParttimeMappings[fullOrParttimeDefault]}")
#                 # Attention: f-Strings are not available, due to Python version being: 3 < Server < 3.6
#                 collectedWorkingTimes = [ fullOrParttimeMappings[fullOrParttimeDefault] ]
#             row[fullOrParttimeNameForWebsite] = ", ".join(collectedWorkingTimes)
#             # ... and writing it to CSV
#             dw.writerow(row)
# except:
#     print("Writing CSV failed.")
#     exit(1) 
import csv
import html
import re
from datetime import datetime

class JobMarkdownConverter:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.job_or_trainee_mappings = {
            "2": "Auszubildendenstelle",
            "6": "Festanstellung",
            "fe9a669ca70d49a88d972a860742b379": "Aushilfe"
        }
        self.job_or_trainee_default = "6"
        self.job_or_trainee_category_name = "Stellentyp"
        self.full_or_parttime_mappings = {
            "799eb9d2c0bc4e7490fde05f847b331a": "in Teilzeit",
            "137caf67764c4b63b0272895af1704b0": "in Vollzeit",
            "87af1987840d4442b87f2e0ee3344a1f": "in Voll- oder Teilzeit"
        }
        self.full_or_parttime_default = "137caf67764c4b63b0272895af1704b0"
        self.full_or_parttime_name = "Arbeitszeit"
        self.jobexperience_mappings = {
            "1b4f51fe628c4119a2d7a581557d0944": "mit Berufserfahrung"
        }
    
    def read_csv(self):
        with open(self.csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            job_listings = list(reader)
        return job_listings
    
    def convert_to_markdown(self, job_listings):
        markdown_content = ""
        for job in job_listings:
            markdown_content += f"### {job['externalPostingName']}\n\n"
            markdown_content += f"**Wo?** {job['geo_name']}"
            if job['geo_country'] not in job['geo_name']:
                markdown_content += f", {job['geo_country']}"
            markdown_content += "\n"
            markdown_content += f"**Wer?** {"/".join(self.jobexperience_mappings[x] for x in eval(job['workExperiences']))}\n"
            markdown_content += f"**Wie?** {"/".join(self.job_or_trainee_mappings[x] for x in eval(job['employmentTypes']))} {"/".join(self.full_or_parttime_mappings[x] for x in eval(job['workTimes']))}\n"
            markdown_content += f"**Wie genau?** {self.translate_remote_status(job['remote_status'])}\n"
            summary = self.summarize_description(job['jobAdText'])
            markdown_content += f"**Was? (automatisch gekürzt)** {summary} ...\n"
            markdown_content += f"**Was jetzt?** [Vollständige Beschreibung, alle Infos](https://brandad.softgarden.io/job/{job['jobDbId']}) oder [direkt bewerben]({job['applyOnlineLink']})\n"
            markdown_content += "\n---\n\n"
        return markdown_content
    
    def save_to_markdown_file(self, markdown_content, output_file='jobs.md'):
        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print(f"Markdown file saved as {output_file}")
    
    def summarize_description(self, description):
        text = re.sub('<[^<]+?>', '', description)  # Remove HTML tags
        text = html.unescape(text)  # Decode HTML entities
        sentences = self.split_into_sentences(text)  # Split text into sentences
        # Take the first two sentences for a summary or less if there aren't two full sentences
        summary = ' '.join(sentences[:2])
        return summary.strip().replace("\n\n", "\n")
    
    def interpret_codes(self, field_value):
        # Assuming the field_value could be interpreted with a dictionary or similar structure
        mapping_dict = {
            '6': 'Full-time',
            '137caf67764c4b63b0272895af1704b0': 'Full-time',
            '87af1987840d4442b87f2e0ee3344a1f': 'Part-time or Full-time',
            '22': 'Experienced',
            # Add other mappings here
        }
        values = [mapping_dict.get(str(val), 'Unknown') for val in field_value.strip('[]').split(',')]
        return ', '.join(values).replace("'", "")
    
    def translate_remote_status(self, status):
        return 'flexibles Arbeiten von Zuhause aus möglich' if status == 'REMOTE_FLEXIBLE' else 'Vor-Ort-Präsenz erforderlich'
    
    def process_jobs(self):
        job_listings = self.read_csv()
        markdown_content = self.convert_to_markdown(job_listings)
        self.save_to_markdown_file(markdown_content)

    def split_into_sentences(self, text: str) -> list[str]:
        """
        Split the text into sentences.

        If the text contains substrings "<prd>" or "<stop>", they would lead 
        to incorrect splitting because they are used as markers for splitting.

        :param text: text to be split into sentences
        :type text: str

        :return: list of sentences
        :rtype: list[str]
        """
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He.s|She.s|It.s|They.s|Their.s|Our.s|We.s|But.s|However.s|That.s|This.s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov|edu|me)"
        digits = "([0-9])"
        multiple_dots = r'\.{2,}'
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
        text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\\s" + alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        if sentences and not sentences[-1]: sentences = sentences[:-1]
        return sentences

    def merge_markdown_files(self, merge_source, merge_target):
        pattern = r"---.+?##\ aktuelle\ Jobs.*$"
        pattern = re.compile(pattern, re.DOTALL | re.UNICODE)

        with open(merge_source, "r") as file:
            merge_content = str(file.read())
        with open(merge_target, "r") as file:
            target_content = str(file.read())
        date = datetime.now().strftime("%Y-%m-%d, %H:%M")
        sub = f"---\n\n## aktuelle Jobs (zuletzt aktualisiert: { date })\n\n"
        sub = f"{sub}{merge_content}" 

        if pattern.search(target_content):
            result = pattern.sub(sub, target_content)
        else:
            result = f"{target_content}\n\n{sub}"

        with open(merge_target, "w") as file:
            file.write(f'{result.strip()}\n')
            print("README.md written")

# Example usage:
# converter = JobMarkdownConverter('path_to_job_listings.csv')
# converter.process_jobs()

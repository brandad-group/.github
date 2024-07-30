import job_fetcher
import markdown_converter
import ftp_uploader
from pathlib import Path
import os
from dotenv import load_dotenv

env_file_path = os.environ.get('GITHUB_ENV', None)
if env_file_path is None:
    load_dotenv()

p = Path(__file__).resolve().parent
jf = job_fetcher.JobFetcher(
    p / "jobs.csv",
    os.environ.get("CLIENT_ID"),
    os.environ.get("PASSWORD"),
    os.environ.get("API_PATH")
)
converter = markdown_converter.JobMarkdownConverter(p / "jobs.csv")
ftp = ftp_uploader.FTPUploader(
    os.getenv("FTP_SERVER"),
    os.getenv("FTP_USER"),
    os.getenv("FTP_PASSWORD")
)

jf.fetch_jobs()
jobs = converter.read_csv()
converter.save_to_markdown_file(converter.convert_to_markdown(jobs), p / ".." / "jobs" / "jobs.md")
converter.merge_markdown_files(p / ".." / "jobs" / "jobs.md", p / ".." / "profile" / "README.md")

if ftp.upload(p / "jobs.csv"):
    print("Upload successful")
else:
    print("Upload failed")

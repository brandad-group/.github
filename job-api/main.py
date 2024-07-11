import job_fetcher
import markdown_converter
import ftp_uploader
from pathlib import Path

p = Path(__file__).parent.resolve()
jf = job_fetcher.JobFetcher(p / "jobs.csv")
converter = markdown_converter.JobMarkdownConverter(p / "jobs.csv")
ftp = ftp_uploader.FTPUploader()

jf.fetch_jobs()
jobs = converter.read_csv()
converter.save_to_markdown_file(converter.convert_to_markdown(jobs), p / ".." / "jobs" / "jobs.md")
converter.merge_markdown_files(p / ".." / "jobs" / "jobs.md", p / ".." / "profile" / "README.md")

if ftp.upload(p / "jobs.csv"):
    print("Upload successful")
else:
    print("Upload failed")

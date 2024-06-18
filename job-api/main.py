import job_fetcher
import markdown_converter
from pathlib import Path

# Example usage:
# converter = JobMarkdownConverter('path_to_job_listings.csv')
# converter.process_jobs()

p = Path(__file__).parent.resolve()
jf = job_fetcher.JobFetcher(p / "jobs.csv")
converter = markdown_converter.JobMarkdownConverter(p / "jobs.csv")
jf.fetch_jobs()
jobs = converter.read_csv()
converter.save_to_markdown_file(converter.convert_to_markdown(jobs), p / "jobs.md")
converter.merge_markdown_files(p / "jobs.md", p / ".." / "profile" / "README.md")
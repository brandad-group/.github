import job_fetcher
import markdown_converter

# Example usage:
# converter = JobMarkdownConverter('path_to_job_listings.csv')
# converter.process_jobs()

jf = job_fetcher.JobFetcher("jobs.csv")
converter = markdown_converter.JobMarkdownConverter("jobs.csv")
jf.fetch_jobs()
jobs = converter.read_csv()
converter.save_to_markdown_file(converter.convert_to_markdown(jobs), "jobs.md")
converter.merge_markdown_files("jobs.md", "../profile/README.md")
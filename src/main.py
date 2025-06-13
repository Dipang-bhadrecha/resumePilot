from agents.job_agent import JobAgent

def main():
    agent = JobAgent()
    job_url = input("Paste verified job application URL: ")
    agent.apply_to_job(job_url)

if __name__ == "__main__":
    main()

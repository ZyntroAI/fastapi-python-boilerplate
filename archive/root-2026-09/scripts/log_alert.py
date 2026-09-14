from jira import JIRA

class JiraIntegration:
    def __init__(self):
        self.url = os.getenv("JIRA_URL", "")
        self.email = os.getenv("JIRA_EMAIL", "")
        self.api_token = os.getenv("JIRA_TOKEN", "")
        self.project_key = os.getenv("JIRA_PROJECT", "SEC")
        self.jira = JIRA(server=self.url, basic_auth=(self.email, self.api_token)) if self.url else None

    def create_incident(self, title: str, desc: str, priority: str = "High") -> str | None:
        if not self.jira: return None
        try:
            issue = self.jira.create_issue(
                project=self.project_key,
                summary=title,
                description=desc,
                issuetype={"name": "Incident"},
                priority={"name": priority}
            )
            return f"{self.url}/browse/{issue.key}"
        except Exception as e:
            print(f"Jira Error: {e}")
            return None
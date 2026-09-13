class LogAlertManager:
    def __init__(self):
        self.slack = SlackNotifier(...)
        self.sms = SMSNotifier()
        self.phone = PhoneCaller()
        self.jira = JiraIntegration()
        self.pager = PagerDutyIntegration()

    def send_alert(self, title: str, details: list[str], level: str = "CRITICAL", log_ref: str = ""):
        # 1. Slack
        self.slack.send(title, details, level, log_ref)
        
        # 2. Jira (ทุกเหตุการณ์สำคัญ)
        jira_link = self.jira.create_incident(title, "\n".join(details)) if level in ["CRITICAL", "ERROR"] else None
        
        # 3. PagerDuty + SMS + โทร (เฉพาะวิกฤต)
        if level == "CRITICAL":
            self.sms.send(f"{title} | {details[0]}", urgent=True)
            self.phone.call(title)
            self.pager.trigger(title, {"details": details, "log": log_ref}, links=[{"href": jira_link, "text": "Jira Issue"}] if jira_link else [])

        return {"jira": jira_link}
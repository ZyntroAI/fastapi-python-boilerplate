from enum import Enum


class HookEvent(str, Enum):
    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Chat events
    CHAT_CREATED = "chat.created"
    CHAT_UPDATED = "chat.updated"
    CHAT_SUMMARIZED = "chat.summarized"

    # Backend/API events
    API_CREATED = "api.created"
    API_UPDATED = "api.updated"

    # Security events
    SECURITY_ALERT = "security.alert"
    SECURITY_LOGIN = "security.login"
    SECURITY_LOGOUT = "security.logout"

    # Deployment events
    DEPLOY_STARTED = "deploy.started"
    DEPLOY_FINISHED = "deploy.finished"
    DEPLOY_FAILED = "deploy.failed"

    def __str__(self) -> str:
        return self.value

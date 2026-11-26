from enum import Enum

class HookEvent(str, Enum): TASK_CREATED = "task.created" TASK_UPDATED = "task.updated" CHAT_CREATED = "chat.created" CHAT_SUMMARIZED = "chat.summarized" API_CREATED = "api.created" SECURITY_ALERT = "security.alert" DEPLOY_STARTED = "deploy.started" DEPLOY_FINISHED = "deploy.finished"  

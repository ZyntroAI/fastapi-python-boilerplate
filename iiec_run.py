from typing import List, Optional

class UserCustomization:
def init(self):
# UI customization defaults
self.theme = "light" # options: light, dark, custom
self.custom_colors = {}
self.font_size = 12
self.font_style = "Arial"

# Functional customization defaults
self.notifications_enabled = True
self.notification_methods = ["sound", "popup"]
self.shortcuts = {}
self.language = "en"
self.region = "US"

# Content and interaction defaults
self.personalized_content = True
self.privacy_settings = {
"data_sharing": False,
"profile_visibility": "friends_only"
}
self.chatbot_behavior = {
"tone": "friendly",
"proactive_suggestions": True
}

# Account and profile defaults
self.profile = {
"avatar": None,
"display_name": "User",
"personal_info": {}
}
self.security_settings = {
"two_factor_auth": False,
"password_last_changed": None,
"login_activity": []
}
self.integrations = []

# UI Customization workflows
def set_theme(self, theme: str, custom_colors: Optional[dict] = None):
if theme not in ["light", "dark", "custom"]:
raise ValueError("Invalid theme option")
self.theme = theme
if theme == "custom" and custom_colors:
self.custom_colors = custom_colors
print(f"Theme set to {self.theme} with colors {self.custom_colors}")

def set_font(self, size: int, style: str):
self.font_size = size
self.font_style = style
print(f"Font set to {self.font_style} with size {self.font_size}")

# Functional customization workflows
def configure_notifications(self, enabled: bool, methods: List[str]):
self.notifications_enabled = enabled
self.notification_methods = methods
print(f"Notifications {'enabled' if enabled else 'disabled'} with methods {methods}")

def set_shortcut(self, action: str, shortcut: str):
self.shortcuts[action] = shortcut
print(f"Shortcut for {action} set to {shortcut}")

def set_language_region(self, language: str, region: str):
self.language = language
self.region = region
print(f"Language set to {language}, region set to {region}")

# Content and interaction workflows
def set_privacy(self, data_sharing: bool, profile_visibility: str):
self.privacy_settings["data_sharing"] = data_sharing
self.privacy_settings["profile_visibility"] = profile_visibility
print(f"Privacy settings updated: data_sharing={data_sharing}, profile_visibility={profile_visibility}")

def set_chatbot_behavior(self, tone: str, proactive_suggestions: bool):
self.chatbot_behavior["tone"] = tone
self.chatbot_behavior["proactive_suggestions"] = proactive_suggestions
print(f"Chatbot behavior set to tone={tone}, proactive_suggestions={proactive_suggestions}")

# Account and profile workflows
def update_profile(self, avatar: Optional[str], display_name: str, personal_info: dict):
self.profile["avatar"] = avatar
self.profile["display_name"] = display_name
self.profile["personal_info"] = personal_info
print(f"Profile updated: display_name={display_name}, avatar={avatar}")

def enable_two_factor_auth(self, enabled: bool):
self.security_settings["two_factor_auth"] = enabled
print(f"Two-factor authentication {'enabled' if enabled else 'disabled'}")

def add_integration(self, service_name: str):
if service_name not in self.integrations:
self.integrations.append(service_name)
print(f"Integration added: {service_name}")
else:
print(f"Integration {service_name} already exists")

# Example method to show current settings
def show_settings(self):
import pprint
pprint.pprint(self.dict)

Example usage
if name == "main":
user_custom = UserCustomization()
user_custom.set_theme("dark")
user_custom.set_font(14, "Helvetica")
user_custom.configure_notifications(True, ["email", "popup"])
user_custom.set_shortcut("save", "Ctrl+S")
user_custom.set_language_region("fr", "FR")
user_custom.set_privacy(data_sharing=True, profile_visibility="public")
user_custom.set_chatbot_behavior("professional", False)
user_custom.update_profile(avatar="avatar.png", display_name="Alice", personal_info={"email": "alice@example.com"})
user_custom.enable_two_factor_auth(True)
user_custom.add_integration("Google Drive")
user_custom.show_settings()

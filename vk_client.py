import random

import requests
from pydantic_settings import BaseSettings, SettingsConfigDict


class VKClientConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VK_API_")

    TOKEN: str
    RECIPIENT_ID: int
    VK_API_VERSION: str = "5.199"

class VKClient:
    def __init__(self, config: VKClientConfig):
        self.config = config

    def send_message(self, message: str):
        url = "https://api.vk.ru/method/messages.send"

        params = {
            "message": message,
            "peer_id": self.config.RECIPIENT_ID,
            "access_token": self.config.TOKEN,
            "v": self.config.VK_API_VERSION,
            "random_id": random.randint(1, 2147483647)
        }

        requests.get(url, params=params)

from dotenv import load_dotenv # type: ignore
import os

class Config:
    def __init__(self):
        load_dotenv()
        self.bot_token: str = os.getenv("BOT_TOKEN")
        self.admin_id: list = [int(x) for x in os.getenv("ADMIN_ID").split(",")]

config = Config()
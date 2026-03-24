import os
from dotenv import load_dotenv

load_dotenv()


class Configuration:
    BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
    EMAIL = os.getenv("CONFLUENCE_EMAIL")
    API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
    SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
    PARENT_PAGE_ID = int(os.getenv("CONFLUENCE_PARENT_PAGE_ID", 0))
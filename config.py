from dotenv import load_dotenv
import os
import getpass as getpass

load_dotenv()

CHUNK_SIZE = 2400
CHUNK_OVERLAP = 200


def set_envs():
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass(os.getenv("GOOGLE_API_KEY"))

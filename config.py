import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

WORKDIR = Path(os.getenv("WORKDIR", "output"))
WORKDIR.mkdir(parents=True, exist_ok=True)
SADTALKER_DIR = os.getenv("SADTALKER_DIR", "./SadTalker")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "stabilityai/sdxl-turbo")
MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", "2"))

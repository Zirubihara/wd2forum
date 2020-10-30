import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATEBASE_URL", "sqlite:///localhost.sqlite"))
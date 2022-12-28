from .db import AsyncDB
from ..config import settings

db = AsyncDB(settings.dsn, min_size=5, max_size=20)
import os
try:
    os.remove('database.db')
except FileNotFoundError as e:
    pass
from osiris import init_db
init_db()

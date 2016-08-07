# aiohttp settings
PORT = 8853
TEMPLATES_PATH = 'templates'
STATIC_PATH = 'static'

# data persistence
SHELVE_FILENAME = 'current_state.db'

# postgresql settings
POSTGRES_CONNECTION_SETTINGS = {
    'database': 'eblank',
    'user': 'eblank',
    'password': 'i_am_password',
    'host': 'localhost',
    'port': 5432,
}

# APP settings
HOUR_PRICE = 15  # UAH

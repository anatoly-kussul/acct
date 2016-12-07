# aiohttp settings
PORT = 8853
TEMPLATES_PATH = 'web/templates'
STATIC_PATH = 'web/static'

# data persistence
SHELVE_FILENAME = 'current_state.db'

# postgresql settings
POSTGRES_CONNECTION_SETTINGS = {
    'database': 'eblank',
    'user': 'eblank',
    'password': 'i_am_password',
    'host': 'postgres',
    'port': 5432,
}

# APP settings
HOUR_PRICE = 15  # UAH

import tempfile
db_file = tempfile.NamedTemporaryFile()


class Config(object):
	SECRET_KEY = 'REPLACE ME'


class ProdConfig(Config):
	ENV = 'prod'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

	CACHE_TYPE = 'simple'


class DevConfig(Config):
	ENV = 'dev'
	DEBUG = True
	DEBUG_TB_INTERCEPT_REDIRECTS = False

	SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
	TOR_HOST = '127.0.0.1'
	TOR_PORT = '9050'
	CACHE_TYPE = 'null'
	ASSETS_DEBUG = True


class TestConfig(Config):
	ENV = 'test'
	DEBUG = True
	DEBUG_TB_INTERCEPT_REDIRECTS = False

	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file.name
	SQLALCHEMY_ECHO = True

	CACHE_TYPE = 'null'
	WTF_CSRF_ENABLED = False

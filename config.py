import os

class Config():
    SECRET_KEY = 'wcg'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = '25'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = '332627893@qq.com'
    MAIL_PASSWORD = 'nysetemnmfvacaec'
    MAIL_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:wcg@localhost/itswcg'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/test_flask'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/flask'

config = {
    'development':DevelopmentConfig,
    'testing':TestConfig,
    'production':ProductionConfig,

    'default':DevelopmentConfig
}
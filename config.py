class Config():
    SECRET_KEY = 'wo shi wcg'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = '25'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = '332627893@qq.com'
    MAIL_PASSWORD = 'nysetemnmfvacaec'
    MAIL_DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:wcg@localhost/itswcg'
    SQLALCHEMY_COMMIT_ON_TRARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}
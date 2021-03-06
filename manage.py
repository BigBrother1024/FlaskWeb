#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from app import create_app, db
from app.models import User, Role, Post, Follow, Comment, Reply, Message
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Message=Message,
                Post=Post, Follow=Follow, Comment=Comment, Reply=Reply)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role

    db.create_all()
    Role.insert_roles()

if __name__ == '__main__':
    app.run()

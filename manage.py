from app import create_app, db
from app.models import User, Role, Post, Follow, Comment, Reply, Message
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context(): return dict(app=app, db=db, User=User, Role=Role, Message=Message,
                                      Post=Post, Follow=Follow, Comment=Comment, Reply=Reply)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    from flask_migrate import upgrade
    from app.models import Role, User

    db.drop_all()
    db.create_all()
    Role.insert_roles()
    User.generate_fake(50)
    Post.generate_fake(50)
    Comment.generate_fake(50)
    Reply.generate_fake(50)

if __name__ == '__main__':
    manager.run()

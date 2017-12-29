from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_content():
    return dict(app=app, db=db, User=User,Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_content))
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role

    db.create_all()
	
if __name__ == '__main__':
    app.run()

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server

from main import make_app
from models import db

app = make_app()
manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()

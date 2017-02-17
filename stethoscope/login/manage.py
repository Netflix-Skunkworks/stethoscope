# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

from flask_script import Manager, Shell, Server
import stethoscope.login.factory


manager = Manager(stethoscope.login.factory.create_app)


def main():
  manager.add_command("runserver", Server())
  manager.add_command("shell", Shell())
  manager.run()


if __name__ == "__main__":
  main()

# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

from .factory import create_app


if __name__ == "__main__":
  app = create_app()
  app.run("127.0.0.1", 5001)

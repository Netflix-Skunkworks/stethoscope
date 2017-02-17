# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals

import stethoscope.api.factory

app = stethoscope.api.factory.create_app()
resource = app.resource

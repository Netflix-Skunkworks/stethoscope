# vim: set fileencoding=utf-8 :

from __future__ import absolute_import, print_function, unicode_literals


def get_photo_url(raw):
  image_url = raw['item'].get('image_url', raw['item']['config'].get('image_url'))
  photo_id = raw['item'].get('photo_id', raw['item']['config'].get('photo_id'))
  if image_url is not None:
    return image_url
  elif photo_id is not None:
    return 'https://app.bitfit.com/api/attachments/{:d}/download?scale=tiny'.format(photo_id)
  else:
    return None


def parse_field_list(fields):
  retval = dict()
  for field in fields:
    retval[field['base_name']] = field
  return retval

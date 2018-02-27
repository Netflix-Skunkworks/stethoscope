# vim: set fileencoding=utf-8 :

from pkg_resources import DistributionNotFound, get_distribution


try:
  __version__ = get_distribution(__name__).version
except DistributionNotFound:
  # package is not installed
  pass

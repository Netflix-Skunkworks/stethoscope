# The following is the secret key used by Flask to sign session cookies. It needs to be changed to a
# random value which is kept secret and is unique to your deployment. You should generate a key
# using a cryptographically-secure pseudo-random number generator such as the `os.urandom` Python
# function on modern systems. In short: `os.urandom(24)`.
SECRET_KEY = 'not a secret'

# The following is the secret key used by Stethoscope to secure its API tokens. It needs to be
# changed to a random value which is kept secret and is unique to your deployment. You should
# generate a key using a cryptographically-secure pseudo-random number generator such as the
# `os.urandom` Python function on modern systems. In short: `os.urandom(32)`.
JWT_SECRET_KEY = 'also not a secret'

# For this example configuration, we're using a no-op authentication provider which treats everyone
# as having successfully authenticated as a privileged user.
LOGIN_MANAGER = 'null'

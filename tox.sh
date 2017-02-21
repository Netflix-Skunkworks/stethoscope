#!/usr/bin/env sh

export PYENV_VERSION='2.7.11:3.3.6:3.4.5:3.5.2:3.6.0'

if which homebrew 2>&1 >/dev/null; then
  export LDFLAGS="-L/usr/local/opt/openssl/lib"
  export CPPFLAGS="-I/usr/local/opt/openssl/include"
  export TOX_TESTENV_PASSENV="LDFLAGS CPPFLAGS"
fi

tox "$@"

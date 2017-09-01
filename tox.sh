#!/usr/bin/env sh

export PYENV_VERSION='2.7.13:3.4.6:3.5.3:3.6.2'

if which brew 2>&1 >/dev/null; then
  export LDFLAGS="-L$(brew --prefix openssl)/lib"
  export CPPFLAGS="-I$(brew --prefix openssl)/include"
  export TOX_TESTENV_PASSENV="LDFLAGS CPPFLAGS"
fi

tox "$@"

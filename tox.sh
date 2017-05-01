#!/usr/bin/env sh

export PYENV_VERSION='2.7.11:3.4.5:3.5.2:3.6.0'

if which brew 2>&1 >/dev/null; then
  export LDFLAGS="-L$(brew --prefix openssl)/lib"
  export CPPFLAGS="-I$(brew --prefix openssl)/include"
  export TOX_TESTENV_PASSENV="LDFLAGS CPPFLAGS"
fi

tox "$@"

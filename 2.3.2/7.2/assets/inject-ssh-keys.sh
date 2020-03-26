#!/usr/bin/env sh

SSH_DIR=${SSH_DIR:-/.ssh}

# Inject SSH keys if mounted to ${SSH_HOME}
if [[ ! -z ${SSH_DIR} ]] && [[ -d ${SSH_DIR} ]]; then
  cp -R $SSH_DIR $HOME/.ssh
  chmod 700 $HOME/.ssh

  test -f $HOME/.ssh/id_rsa.pub && chmod -f 644 $HOME/.ssh/id_rsa.pub
  test -f $HOME/.ssh/id_rsa && chmod -f 600 $HOME/.ssh/id_rsa
fi
from contextlib import contextmanager
import os
import random
import string

import git
import paramiko
import pytest


REPOS_DIR = '/content/repos'


def _random_string(string_length=10):
  """Generate a random string of fixed length """
  letters = string.ascii_lowercase
  return "".join(random.choice(letters) for i in range(string_length))


@contextmanager
def _as_git_user(user):
  init_ssh_command = os.environ.get('GIT_SSH_COMMAND')
  try:
    os.environ['GIT_SSH_COMMAND'] = f'ssh -i /keys/{user}'
    yield
  finally:
    if init_ssh_command is None:
      del os.environ['GIT_SSH_COMMAND']
    else:
      os.environ['GIT_SSH_COMMAND'] = init_ssh_command

@pytest.fixture
def repo_name():
  name = _random_string()
  
  client = paramiko.SSHClient()
  client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
  client.connect('git', username='test1', pkey=paramiko.RSAKey.from_private_key_file("/keys/test1"))
  client.exec_command(f'init {name}.git')
  client.close()

  for user in ['test1', 'test2']:
    user_repo_path = os.path.join(REPOS_DIR, f'{user}_{name}')
    with _as_git_user(user):
      git.Repo.clone_from(f'ssh://{user}@git/git/data/users/test1/{name}.git', user_repo_path)

  return name

def test_something(repo_name):
  assert repo_name is not None

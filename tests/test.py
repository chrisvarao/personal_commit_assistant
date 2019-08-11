import os
import random
import string

import git
import paramiko
import pytest


REPOS_DIR = '/content/repos'


def random_string(string_length=10):
  """Generate a random string of fixed length """
  letters = string.ascii_lowercase
  return "".join(random.choice(letters) for i in range(string_length))


@pytest.fixture
def repo_name():
  name = random_string()
  
  client = paramiko.SSHClient()
  client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
  client.connect('git', username='test1', pkey=paramiko.RSAKey.from_private_key_file("/keys/test1"))
  client.exec_command(f'init {name}.git')
  client.close()

  for user in ['test1', 'test2']:
    user_repo_path = os.path.join(REPOS_DIR, f'{user}_{name}')
    git.Repo.clone_from(f'ssh://{user}@git/git/data/users/test1/{name}.git', user_repo_path, env={"GIT_SSH_COMMAND": f'ssh -i /keys/{user}'})

  return name

def test_something(repo_name):
  assert repo_name is not None

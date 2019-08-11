import os
import random
import string

import git
import paramiko


REPOS_DIR = '/content/repos'


def random_string(string_length=10):
  """Generate a random string of fixed length """
  letters = string.ascii_lowercase
  return "".join(random.choice(letters) for i in range(string_length))


def init_repo():
  repo_name = random_string()
  
  client = paramiko.SSHClient()
  client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
  client.connect('git', username='test1')
  client.exec_command(f'init {repo_name}.git')
  client.close()

  for user in ['test1', 'test2']:
    user_repo_path = os.path.join(REPOS_DIR, f'{user}_{repo_name}')
    git.Repo.clone_from(f'ssh://{user}@git/git/data/users/test1/{repo_name}.git', user_repo_path)

  return repo_name

if __name__ == '__main__':
  init_repo()
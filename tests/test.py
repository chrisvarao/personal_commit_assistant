from contextlib import contextmanager
import os
import random
import string

import git
import paramiko
import pytest

from assistant import questions, todos, utils


REPOS_DIR = "/content/repos"


def _random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(string_length))


@contextmanager
def _as_git_user(user, repo_name):
    user_repo_path = os.path.join(REPOS_DIR, f"{user}_{repo_name}")
    init_ssh_command = os.environ.get("GIT_SSH_COMMAND")
    init_dir = os.getcwd()
    try:
        os.environ["GIT_SSH_COMMAND"] = f"ssh -i /keys/{user}"
        os.chdir(user_repo_path)
        yield
    finally:
        os.chdir(init_dir)
        if init_ssh_command is None:
            del os.environ["GIT_SSH_COMMAND"]
        else:
            os.environ["GIT_SSH_COMMAND"] = init_ssh_command


@pytest.fixture
def repo_name():
    name = _random_string()

    client = paramiko.SSHClient()
    client.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
    client.connect("git", username="test1", pkey=paramiko.RSAKey.from_private_key_file("/keys/test1"))
    client.exec_command(f"init {name}.git")
    client.close()

    for user in ["test1", "test2"]:
        user_repo_path = os.path.join(REPOS_DIR, f"{user}_{name}")
        os.environ["GIT_SSH_COMMAND"] = f"ssh -i /keys/{user}"
        git.Repo.clone_from(f"ssh://{user}@git/git/data/users/test1/{name}.git", user_repo_path)

    return name


def test_initialization(repo_name):
    assert repo_name is not None
    with _as_git_user("test1", repo_name):
        utils.setup_pre_commit()
        assert os.path.exists(".assistant.ini")
        assert os.path.exists(".git/hooks/run_personal_commit_assistant")

import collections
import configparser
from contextlib import contextmanager
import json
import os
import random
import string
from unittest import mock

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


def test_setup_pre_commit(repo_name):
    with _as_git_user("test1", repo_name):
        utils.setup_pre_commit()
        assert os.path.exists(".git/hooks/run_personal_commit_assistant")
        pre_commit_contents = None
        with open(".git/hooks/pre-commit", "r") as file:
            pre_commit_contents = file.read()

        utils.setup_pre_commit()
        with open(".git/hooks/pre-commit", "r") as file:
            assert pre_commit_contents == file.read()


def test_init_assistant_file(repo_name):
    with _as_git_user("test1", repo_name):
        utils.init_assistant_file()
        assert os.path.exists(".assistant.ini")


def test_question_without_script_raises_error(repo_name):
    with _as_git_user("test1", repo_name):
        with pytest.raises(Exception) as e_info:
            questions.run_questionnaire(".assistant.ini")
        assert e_info.value.args[0] == "Assistant config file '.assistant.ini' doesn't exist."


def test_question_condition_valid_operator(repo_name):
    config = configparser.ConfigParser()
    config["question.commit_kind"] = collections.OrderedDict(
        {"prompt": "What kind of commit is this?", "answer_type": "multiple_choice"}
    )

    config["choices.commit_kind"] = collections.OrderedDict(
        {"bug_fix": "bug fix", "new_functionality": "new functionality"}
    )

    config["question.bug_description"] = collections.OrderedDict(
        {"prompt": "What bug is being fixed?", "only": "commit_kind.equals.bug_fix", "answer_type": "text"}
    )

    with _as_git_user("test1", repo_name):
        with open(".assistant.ini", "w+") as config_file:
            config.write(config_file)
        with mock.patch("pick.pick", return_value=("bug_fix", None)), mock.patch(
            "assistant.utils.read_line", return_value="a big bug"
        ):
            questions.run_questionnaire(".assistant.ini")
        with open(".assistant_store/master.current_responses.json", "r") as response_file:
            assert json.loads(response_file.read()) == {
                "commit_id": "initial",
                "answers": {"bug_description": "a big bug", "commit_kind": "bug_fix"},
            }


def test_todo_question(repo_name):
    config = configparser.ConfigParser()

    config["question.bug_description"] = collections.OrderedDict(
        {"prompt": "What bug is being fixed?", "answer_type": "text"}
    )

    config["question.bug_fix_unit_tests"] = {
        "prompt": "What unit tests are needed?",
        "answer_type": "todo",
        "todo_group": "Unit tests for bug fixes",
        "todo_for": 'Bug fix "{bug_description}"',
    }

    with _as_git_user("test1", repo_name):
        with open(".assistant.ini", "w+") as config_file:
            config.write(config_file)
        with mock.patch("pick.pick", return_value=("bug_fix", None)), mock.patch(
            "assistant.utils.read_line", side_effect=["a big bug", "test for a", "test for b", ""]
        ):
            questions.run_questionnaire(".assistant.ini")
        with open(".assistant_store/master.current_responses.json", "r") as response_file:
            assert json.loads(response_file.read()) == {
                "commit_id": "initial",
                "answers": {"bug_description": "a big bug", "bug_fix_unit_tests": ["test for a", "test for b"]},
                "todos": {
                    "Unit tests for bug fixes": {'Bug fix "a big bug"': [["test for a", False], ["test for b", False]]}
                },
            }

        with mock.patch("pick.pick", side_effect=[("done", None), ("not done", None)]):
            todos.run_todo()

        with open(".assistant_store/master.current_responses.json", "r") as response_file:
            assert json.loads(response_file.read()) == {
                "commit_id": "initial",
                "answers": {"bug_description": "a big bug", "bug_fix_unit_tests": ["test for a", "test for b"]},
                "todos": {
                    "Unit tests for bug fixes": {'Bug fix "a big bug"': [["test for a", True], ["test for b", False]]}
                },
            }


def test_question_condition_invalid_operator(repo_name):
    config = configparser.ConfigParser()
    config["question.commit_kind"] = collections.OrderedDict(
        {"prompt": "What kind of commit is this?", "answer_type": "multiple_choice"}
    )

    config["choices.commit_kind"] = collections.OrderedDict(
        {"bug_fix": "bug fix", "new_functionality": "new functionality"}
    )

    config["question.bug_description"] = collections.OrderedDict(
        {
            "prompt": "What bug is being fixed?",
            "only": "commit_kind.fouriertransformequals.bug_fix",
            "answer_type": "text",
        }
    )

    with _as_git_user("test1", repo_name):
        with open(".assistant.ini", "w+") as config_file:
            config.write(config_file)
        with pytest.raises(Exception) as e_info:
            with mock.patch("pick.pick", return_value=("bug_fix", None)):
                questions.run_questionnaire(".assistant.ini")
        assert e_info.value.args[0] == "Invalid conditional operator fouriertransformequals."


def test_question_condition_unasked_question(repo_name):
    config = configparser.ConfigParser()
    config["question.bug_description"] = collections.OrderedDict(
        {"prompt": "What bug is being fixed?", "only": "commit_kind.equals.bug_fix", "answer_type": "text"}
    )

    with _as_git_user("test1", repo_name):
        with open(".assistant.ini", "w+") as config_file:
            config.write(config_file)
        with pytest.raises(Exception) as e_info:
            with mock.patch("pick.pick", return_value=("bug_fix", None)):
                questions.run_questionnaire(".assistant.ini")
        assert e_info.value.args[0] == "The question 'commit_kind' hasn't been asked."

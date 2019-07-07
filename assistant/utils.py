import git
import json
import os
import platform
import readline
import sys

from assistant import constants


def get_commit_info():
    repo = git.Repo(".")
    config_reader = repo.config_reader()
    branch_name = repo.head.reference.name
    try:
        author = config_reader.get_value("user", "name")
        commit_id = next(repo.iter_commits(f"origin/{branch_name}", max_count=1, author=author))
        return branch_name, commit_id
    except:
        return branch_name, "initial"


def setup_directory_for_git_ref():
    repo = git.Repo(".")
    branch_name = repo.head.reference.name

    if not os.path.exists(constants.ASSISTANT_STORE_DIR):
        os.mkdir(constants.ASSISTANT_STORE_DIR)

    branch_dir = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}"
    if not os.path.exists(branch_dir):
        os.mkdir(branch_dir)

    answers_dir = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}/answers"
    if not os.path.exists(answers_dir):
        os.mkdir(answers_dir)

    todo_dir = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}/todos"
    if not os.path.exists(todo_dir):
        os.mkdir(todo_dir)


def read_line(prefill=""):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input()
    finally:
        readline.set_startup_hook()

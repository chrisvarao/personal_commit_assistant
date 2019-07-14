import collections
import configparser
import git
import json
import os
import platform
import readline
import shutil
import stat
import sys

from assistant import constants, default_config


_needs_fetch = True


def get_commit_info():
    repo = git.Repo(".")
    global _needs_fetch
    if _needs_fetch:
        repo.remotes.origin.fetch()
        _needs_fetch = False
    config_reader = repo.config_reader()
    branch_name = repo.head.reference.name
    try:
        author = config_reader.get_value("user", "name")
        commit = next(repo.iter_commits(f"origin/{branch_name}", max_count=1, author=author))
        return branch_name, commit.name_rev.split(" ")[0]
    except:
        return branch_name, "initial"


def read_file_as_ordered_dict(file_name):
    try:
        with open(file_name, "r") as file:
            return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(file.read() or "{}")
    except:
        return collections.OrderedDict()


def rotate_files():
    branch_name, commit_id = get_commit_info()
    current_response_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.current_responses.json"
    current_response = read_file_as_ordered_dict(current_response_file)
    todos = current_response.get("todos", collections.OrderedDict())
    remaining_todos = collections.OrderedDict()
    for group, for_group in todos.items():
        for item, for_item in for_group.items():
            for todo in for_item:
                if todo[1]:
                    continue
                remaining_todos[group] = remaining_todos.get(group, collections.OrderedDict())
                remaining_todos[group][item] = remaining_todos[group].get(item, [])
                remaining_todos[group][item].append(todo)
    branch_todos_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.todos.json"
    with open(branch_todos_file, "w+") as branch_todos_file:
        branch_todos_file.write(json.dumps(remaining_todos))
    with open(current_response_file, "w+") as current_response_file:
        current_response_file.write(json.dumps({"commit_id": commit_id, "answers": {}, "todos": {}}))
    assistant_config_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.assistant.ini"
    if os.path.exists(assistant_config_file):
        os.remove(assistant_config_file)


def setup_response_files():
    branch_name, commit_id = get_commit_info()
    if not os.path.exists(constants.ASSISTANT_STORE_DIR):
        os.mkdir(constants.ASSISTANT_STORE_DIR)

    current_response_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.current_responses.json"
    current_response = read_file_as_ordered_dict(current_response_file)
    if "commit_id" in current_response and current_response["commit_id"] != commit_id:
        rotate_files()


def setup_config_file(source_config_file_name):
    branch_name, _ = get_commit_info()
    config_file_name = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.assistant.ini"
    if not os.path.exists(config_file_name):
        shutil.copyfile(source_config_file_name, config_file_name)


def get_saved_response():
    branch_name, _ = get_commit_info()
    current_response_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.current_responses.json"
    return read_file_as_ordered_dict(current_response_file)


def update_saved_response(answers=None, todos=None):
    branch_name, commit_id = get_commit_info()
    current_response_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.current_responses.json"
    current_response = read_file_as_ordered_dict(current_response_file)
    current_response["commit_id"] = commit_id
    if answers:
        current_response["answers"] = answers
    if todos:
        current_response["todos"] = todos
    with open(current_response_file, "w+") as current_response_file:
        current_response_file.write(json.dumps(current_response))


def clear_files_for_commit():
    branch_name, _ = get_commit_info()
    files = [
        f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.current_responses.json",
        f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.assistant.ini",
    ]
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def get_config():
    branch_name, _ = get_commit_info()
    config_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.assistant.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def read_line(prefill=""):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input()
    finally:
        readline.set_startup_hook()

def setup_pre_commit():
    if os.path.exists(".git/hooks/run_personal_commit_assistant"):
        return
    with open(".assistant.ini", "w+") as config_file:
        config_file.write(default_config.DEFAULT_CONFIG)
    with open(".git/hooks/run_personal_commit_assistant", "w+") as script:
        script.write("personal_commit_assistant question < /dev/tty")
    os.chmod(".git/hooks/run_personal_commit_assistant", stat.S_IRWXU)
    pre_commit_exists = os.path.exists(".git/hooks/pre-commit")
    write_mode = "w" if pre_commit_exists else "a"
    if pre_commit_exists:
        shutil.copyfile(".git/hooks/pre-commit", ".git/hooks/pre-commit.copy")
    with open(".git/hooks/pre-commit", write_mode) as pre_commit_script:
        pre_commit_script.write("\n$(dirname $0)/run_personal_commit_assistant")
    if not pre_commit_exists:
        os.chmod(".git/hooks/pre-commit", stat.S_IRWXU)

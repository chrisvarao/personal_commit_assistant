import collections
import json

import pick

from assistant import constants, utils


def save_todos_from_answers(questions, answers):
    branch_name, commit_id = utils.get_commit_info()
    file_for_commit = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}/todos/{commit_id}"
    file_contents = collections.OrderedDict()
    for question_name, question_options in questions.items():
        if question_options["answer_type"] != constants.AnswerTypes.TODO or question_name not in answers:
            continue
        todo_for_key = question_options.get("todo_for", "").format(**answers)
        todo_group_key = question_options.get("todo_group", "")
        todo_group = file_contents[todo_group_key] = file_contents.get(todo_group_key, collections.OrderedDict())
        todo_for = todo_group[todo_for_key] = todo_group.get(todo_for_key, [])
        for item in answers[question_name]:
            todo_for.append([item, False])
    with open(file_for_commit, "w+") as file:
        file.write(json.dumps(file_contents))


def get_todos_for_commit():
    branch_name, commit_id = utils.get_commit_info()
    file_for_commit = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}/todos/{commit_id}"

    try:
        with open(file_for_commit, "r") as file:
            return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(file.read() or "{}")
    except:
        return collections.OrderedDict()


def run_todo_on_saved_list(todos):
    new_todos = collections.OrderedDict()
    for group, for_group in todos.items():
        for item, for_item in for_group.items():
            result = []
            for todo in for_item:
                choice, _ = pick.pick(["not done", "done"], title=f"{group}:\n    {todo[0]}:")
                if choice == "not done":
                    new_todos[group] = new_todos.get(group, collections.OrderedDict())
                    new_todos[group][item] = new_todos[group].get(item, [])
                    new_todos[group][item].append([todo[0], False])
    return new_todos


def run_todo():
    commit_todos = get_todos_for_commit()
    commit_todos = run_todo_on_saved_list(commit_todos)

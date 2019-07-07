import collections
import json

import pick

from assistant import constants, utils


def save_todos_from_answers(questions, answers):
    branch_name, _ = utils.get_commit_info()
    branch_todos_file = f"{constants.ASSISTANT_STORE_DIR}/{branch_name}.todos.json"
    todos = utils.read_file_as_ordered_dict(branch_todos_file)
    for question_name, question_options in questions.items():
        if question_options["answer_type"] != constants.AnswerTypes.TODO or question_name not in answers:
            continue
        todo_for_key = question_options.get("todo_for", "").format(**answers)
        todo_group_key = question_options.get("todo_group", "")
        todo_group = todos[todo_group_key] = todos.get(todo_group_key, collections.OrderedDict())
        todo_for = todo_group[todo_for_key] = todo_group.get(todo_for_key, [])
        for item in answers[question_name]:
            todo_for.append([item, False])
    utils.update_saved_response(todos=todos)


def get_todos_for_commit():
    return utils.get_saved_response().get("todos", collections.OrderedDict())


def run_todo_on_saved_list(todos):
    new_todos = collections.OrderedDict()
    for group, for_group in todos.items():
        for item, for_item in for_group.items():
            result = []
            for todo in for_item:
                default_index = 1 if todo[1] else 0
                choice, _ = pick.pick(
                    ["not done", "done"], title=f"{group}:\n    {todo[0]}:", default_index=default_index
                )
                new_todos[group] = new_todos.get(group, collections.OrderedDict())
                new_todos[group][item] = new_todos[group].get(item, [])
                new_todos[group][item].append([todo[0], choice == "done"])
    return new_todos


def run_todo():
    todos = get_todos_for_commit()
    todos = run_todo_on_saved_list(todos)
    utils.update_saved_response(todos=todos)

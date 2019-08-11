import collections
import json
import os
import platform

import pick

from assistant import constants, todos, utils


def get_saved_answers():
    return utils.get_saved_response().get("answers", collections.OrderedDict())


def save_answers(answers):
    utils.update_saved_response(answers=answers)


def read_todo_question(saved_todos=[]):
    i = 1
    items = []
    while True:
        print(f"\n{i}. ", end="")
        saved_todo = saved_todos[i - 1] if i <= len(saved_todos) else ""
        prefill = saved_todo
        item = utils.read_line(prefill)
        if not item:
            break
        items.append(item)
        i += 1
    return items


def meets_condition(answers, condition):
    tokens = condition.split(".")
    question_name = tokens[0]
    conditional_op = tokens[1]
    answer = tokens[2]
    if conditional_op == constants.ConditionOps.EQUALS:
        return answers[question_name] == answer
    else:
        raise Exception(f"Invalid conditional operator {conditional_op}")


def run_questionnaire(config_file):
    if not os.path.exists(config_file):
        raise Exception(f"Assistant config file '{config_file}' doesn't exist")

    utils.setup_response_files()
    utils.setup_config_file(config_file)
    saved_answers = get_saved_answers()

    config = utils.get_config()
    questions = collections.OrderedDict()
    answers = collections.OrderedDict()
    for section in config.sections():
        tokens = section.split(".")
        section_type = tokens[0]
        if section_type == "question":
            questions[tokens[1]] = dict(config.items(section))
        elif section_type == "choices":
            questions[tokens[1]]["choices"] = collections.OrderedDict(config.items(section))
        else:
            raise Exception(f"Invalid section name {section}")

    for question_name, question_options in questions.items():
        if "only" in question_options:
            if not meets_condition(answers, question_options["only"]):
                continue

        saved_answer = saved_answers.get(question_name, "")

        prompt = question_options["prompt"]
        answer_type = question_options["answer_type"]
        if answer_type == constants.AnswerTypes.MULTIPLE_CHOICE:
            choices = question_options["choices"]
            default_index = list(choices.keys()).index(saved_answer) if saved_answer else 0
            choice, _ = pick.pick(
                list(choices.keys()),
                title=prompt,
                default_index=default_index,
                options_map_func=lambda choice_key: choices[choice_key],
            )
            answers[question_name] = choice
        elif answer_type == constants.AnswerTypes.TEXT:
            print(f"{prompt}:")
            answers[question_name] = utils.read_line(saved_answer)
        elif answer_type == constants.AnswerTypes.TODO:
            print(f"{prompt}:")
            answers[question_name] = read_todo_question(saved_answer)
        else:
            raise Exception(f'Invalid answer type {question_options["answer_type"]}')

    if platform.system() == "Linux":
        os.system("clear")
    else:
        os.system("cls")

    for question_name, answer in answers.items():
        question_options = questions[question_name]
        answer_type = question_options["answer_type"]
        print(f'{question_options["prompt"]}:\n')
        if answer_type == constants.AnswerTypes.MULTIPLE_CHOICE:
            answer = question_options["choices"][answer]
        print(f"    {answer}\n")
    todos.save_todos_from_answers(questions, answers)
    save_answers(answers)

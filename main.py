import argparse
import collections
import configparser
import json
import os
import platform
import sys

import pick

from assistant import constants

arg_parser = argparse.ArgumentParser(description="Runs personal commit assistant.")
arg_parser.add_argument("task", choices=["question"])
arg_parser.add_argument("--config", "-c", default=".assistant.ini")


def meets_condition(answers, condition):
    tokens = condition.split(".")
    question_name = tokens[0]
    conditional_op = tokens[1]
    answer = tokens[2]
    if conditional_op == constants.ConditionOps.EQUALS:
        return answers[question_name] == answer
    else:
        raise Exception(f"Invalid conditional operator {conditional_op}")


def read_line():
    line, char = "", sys.stdin.read(1)
    while not (char == "\n" or char == "\r" or char == ""):
        line += char
        char = sys.stdin.read(1)
    return line


def read_todo():
    i = 1
    items = []
    while True:
        print(f"\n{i}. ", end="")
        item = read_line()
        if not item:
            break
        done, _ = pick.pick(["yes", "no"], title=f'Is "{item}" complete?')
        items.append((item, done == "yes"))
        i += 1
    return items


def save_todos(questions, answers):
    file_contents = {}
    for question_name, question_options in questions.items():
        if question_options["answer_type"] != constants.AnswerTypes.TODO or question_name not in answers:
            continue
        todo_for_key = question_options.get("todo_for", "").format(**answers)
        todo_group_key = question_options.get("todo_group", "")
        todo_group = file_contents[todo_group_key] = file_contents.get(todo_group_key, {})
        todo_for = todo_group[todo_for_key] = todo_group.get(todo_for_key, [])
        for item in answers[question_name]:
            todo_for.append(list(item))
    with open(".todo", "w+") as file:
        file.write(json.dumps(file_contents))


def run_questionnaire(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
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

        prompt = question_options["prompt"]
        answer_type = question_options["answer_type"]
        if answer_type == constants.AnswerTypes.MULTIPLE_CHOICE:
            choices = question_options["choices"]
            choice, _ = pick.pick(
                list(choices.keys()), title=prompt, options_map_func=lambda choice_key: choices[choice_key]
            )
            answers[question_name] = choice
        elif answer_type == constants.AnswerTypes.TEXT:
            print(f"{prompt}:")
            answers[question_name] = read_line()
        elif answer_type == constants.AnswerTypes.TODO:
            print(f"{prompt}:")
            answers[question_name] = read_todo()
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
    save_todos(questions, answers)


if __name__ == "__main__":
    args = arg_parser.parse_args()
    if args.task == "question":
        run_questionnaire(args.config)

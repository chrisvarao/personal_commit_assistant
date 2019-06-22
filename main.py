import argparse
import collections
import configparser
import sys

import questionnaire

from assistant import constants

arg_parser = argparse.ArgumentParser(description="Runs personal commit assistant.")
arg_parser.add_argument("task", choices=["question"])
arg_parser.add_argument("--config", "-c", default=".assistant.ini")


def run_questionnaire(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    questions = collections.OrderedDict()
    for section in config.sections():
        tokens = section.split(".")
        section_type = tokens[0]
        if section_type == "question":
            questions[tokens[1]] = dict(config.items(section))
        elif section_type == "choices":
            questions[tokens[1]]["choices"] = list(config.items(section))
        else:
            raise Exception(f"Invalid section name {section}")

    q = questionnaire.Questionnaire()
    for question_name, question_options in questions.items():
        answer_type = question_options["answer_type"]
        question = None
        if answer_type == constants.AnswerTypes.MULTIPLE_CHOICE:
            question = q.one(question_name, *question_options["choices"], prompt=question_options["prompt"])
        elif answer_type == constants.AnswerTypes.TEXT:
            question = q.raw(question_name, prompt=question_options["prompt"])
        else:
            raise Exception(f'Invalid answer type {question_options["answer_type"]}')

        if "only" in question_options:
            tokens = question_options["only"].split(".")
            question_name = tokens[0]
            conditional_op = tokens[1]
            question_value = tokens[2]
            if conditional_op == constants.ConditionOps.EQUALS:
                question.condition((question_name, question_value))
            else:
                raise Exception(f"Invalid conditional operator {conditional_op}")
    q.run()
    print(q.format_answers())


if __name__ == "__main__":
    args = arg_parser.parse_args()
    if args.task == "question":
        run_questionnaire(args.config)

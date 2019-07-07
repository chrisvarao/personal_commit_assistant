import argparse
import collections
import configparser
import json
import os
import platform
import readline
import sys

import git
import pick

from assistant import constants, questions, todos, utils

arg_parser = argparse.ArgumentParser(description="Runs personal commit assistant.")
arg_parser.add_argument("task", choices=["question", "todo", "clear", "rotate"])
arg_parser.add_argument("--config", "-c", default=".assistant.ini")

if __name__ == "__main__":
    args = arg_parser.parse_args()
    if args.task == "question":
        questions.run_questionnaire(args.config)
        todos.run_todo()
    elif args.task == "todo":
        todos.run_todo()
    elif args.task == "clear":
        utils.clear_files_for_commit()
    elif args.task == "rotate":
        utils.rotate_files()

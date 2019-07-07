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

from assistant import constants, questions, todos

arg_parser = argparse.ArgumentParser(description="Runs personal commit assistant.")
arg_parser.add_argument("task", choices=["question", "todo"])
arg_parser.add_argument("--config", "-c", default=".assistant.ini")

if __name__ == "__main__":
    args = arg_parser.parse_args()
    if args.task == "question":
        questions.run_questionnaire(args.config)
        todos.run_todo()
    elif args.task == "todo":
        todos.run_todo()

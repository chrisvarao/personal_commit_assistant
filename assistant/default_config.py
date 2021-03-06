DEFAULT_CONFIG = """
[question.commit_kind]
prompt = What kind of commit is this?
answer_type = multiple_choice

[choices.commit_kind]
static_analysis_fix=static analysis fix
bug_fix=bug fix
new_functionality=new functionality
integration_tests=integration tests

[question.bug_description]
prompt = What bug is being fixed?
only = commit_kind.equals.bug_fix
answer_type = text

[question.functionality_description]
prompt = What functionality was added
only = commit_kind.equals.new_functionality
answer_type = text

[question.new_functionality_unit_test]
prompt = What unit tests are needed?
only = commit_kind.equals.new_functionality
answer_type = todo
todo_group = Unit tests for new functionality
todo_for = Functionality "{functionality_description}"

[question.bug_fix_unit_tests]
prompt = What unit tests are needed?
only = commit_kind.equals.bug_fix
answer_type = todo
todo_group = Unit tests for bug fixes
todo_for = Bug fix "{bug_description}"
"""

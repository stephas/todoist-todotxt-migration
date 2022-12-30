import os

import pytest

from datetime import date

from todoist_todotxt_migration.tools import Migration, ProjectRenameStrategy

@pytest.fixture
def filename():
    name = 'todo_integ.txt'
    try:
        os.remove(name)
    except FileNotFoundError:
        pass
    yield name
    os.remove(name)


def test_integ(filename):
    migration = Migration.from_env_secret()
    migration.generate_file(filename)
    migration.clear_cache()
    with open(filename, 'r') as fh:
        assert len(fh.readlines()) > 0


def test_integ_keep_todoist_id(filename):
    migration = Migration.from_env_secret(keep_todoist_id=True)
    migration.generate_file(filename)
    migration.clear_cache()
    with open(filename, 'r') as fh:
        lines = fh.readlines()
        assert len(lines) > 0
        assert "todoist:" in lines[0]

def test_complete_todoist_task_from_todotxt(filename):
    # create test task in todoist
    def _clean_test_task():
        [migration.api.delete_task(task_id=cleanup.id) for cleanup in migration.get_tasks() if cleanup.content == content]
        migration.clear_cache()
    content="completed task integ test sajdkf1234"
    migration = Migration.from_env_secret(keep_todoist_id=True)
    _clean_test_task()
    task = migration.api.add_task(
        content=content,
        due_string="tomorrow",
        due_lang="en",
        priority=4,
        labels=["ignore_scheduler"]
    )
    # make todotxt with single line in it, completing the task
    todotxt_task = migration.transform_task(task)
    def _complete_todotxt_task(t):
        return f"x {date.today().isoformat()} {t}"
    with open(filename, 'w') as fh:
        t = _complete_todotxt_task(todotxt_task)
        fh.write(t + "\n")
    # do it
    migration.complete_todoist_tasks_from_todotxt(filename)
    # make sure task is gone
    assert not [cleanup for cleanup in migration.get_tasks() if cleanup.content == content]
    # optional cleanup
    _clean_test_task()

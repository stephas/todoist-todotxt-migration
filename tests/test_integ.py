import os

import pytest

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


@pytest.mark.skip('integ_skip')
def test_integ(filename):
    migration = Migration.from_env_secret()
    migration.generate_file(filename)
    migration.clear_cache()
    with open(filename, 'r') as fh:
        assert len(fh.readlines()) > 0

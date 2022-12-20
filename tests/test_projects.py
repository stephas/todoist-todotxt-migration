import pytest

from todoist_todotxt_migration.tools import Migration, ProjectRenameStrategy
from todoist_api_python.models import Task, Project

# TBD: test creation date missing

def make_todoist_project(name):
    return Project.from_dict({
        "color": None,
        "id": None,
        "comment_count": None,
        "is_favorite": None,
        "is_shared": None,
        "name": name,
        "url": None,
        "view_style": None,
    })

def make_todoist_task(content, priority, is_completed=False):
    return Task.from_dict({
        "comment_count": None,
        "is_completed": is_completed,
        "content": content,
        "created_at": "2022-12-20T",
        "creator_id": None,
        "description": None,
        "id": None,
        "priority": priority,
        "project_id": None,
        "section_id": None,
        "url": None
    })
    

def make_new_test_case(migration, todoist_task, todoist_project):
    todoist_project.id = 1
    todoist_task.project_id = todoist_project.id

    migration.get_project_by_id_map = lambda: {todoist_project.id: todoist_project}

    return migration


@pytest.fixture
def migration():
    m = Migration(token=None)
    m.get_project_by_id_map = lambda: {}
    return m
    
def test_task_without_project(migration):
    t = make_todoist_task("A task", priority=1)

    todotxt_task = migration.transform_task(t)

    assert todotxt_task == "2022-12-20 A task"


def test_task_with_project(migration):
    t = make_todoist_task("A task", priority=1)
    p = make_todoist_project("Project")
    migration = make_new_test_case(migration, t, p)

    todotxt_task = migration.transform_task(t)

    assert todotxt_task == "2022-12-20 A task +Project"


def test_task_with_spaces_in_project_name(migration):
    """ Todoist allows spaces, but todo.txt doesn't, handle it with a strategy """
    t = make_todoist_task("A task", priority=1)
    p = make_todoist_project("A project")
    migration = make_new_test_case(migration, t, p)

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Underscore)
    assert todotxt_task == "2022-12-20 A task +A_project"

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase)
    assert todotxt_task == "2022-12-20 A task +AProject"


    # funky name
    p = make_todoist_project("A proJec_-t -")
    migration = make_new_test_case(migration, t, p)

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Underscore)
    assert todotxt_task == "2022-12-20 A task +A_proJec_-t_-"

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase)
    assert todotxt_task == "2022-12-20 A task +AProJec_-t-"

    # first word case doesn't get touched
    p = make_todoist_project("a house")
    migration = make_new_test_case(migration, t, p)

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase)
    assert todotxt_task == "2022-12-20 A task +aHouse"

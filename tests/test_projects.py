import pytest

from todoist_todotxt_migration.tools import Migration
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
    t.project_id = p.id
    migration.get_project_by_id_map = lambda: {p.id: p}

    todotxt_task = migration.transform_task(t)

    assert todotxt_task == "2022-12-20 A task +Project"

def test_task_with_spaces_in_project_name(migration):
    pass
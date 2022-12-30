import pytest

from todoist_todotxt_migration.tools import Migration, ProjectRenameStrategy
from todoist_api_python.models import Task, Project, Section, Due

# TBD: test creation date missing

def make_todoist_section(name, id=None, project_id=None):
    return Section.from_dict({
        "id": id,
        "project_id": project_id,
        "name": name,
        "order": None,
    })

def make_todoist_project(name, id=None, parent_id=None):
    return Project.from_dict({
        "color": None,
        "id": id,
        "parent_id": parent_id,
        "comment_count": None,
        "is_favorite": None,
        "is_shared": None,
        "name": name,
        "url": None,
        "view_style": None,
    })

def make_todoist_due(date, string=""):
    return {
        "date": date,
        "is_recurring": bool(string),
        "string": string,
        "datetime": None,
        "timezone": None
    }

def make_todoist_task(content, priority=1, is_completed=False, project_id=None, labels=None, section_id=None, due=None, created_at="2022-12-20"):
    return Task.from_dict({
        "comment_count": None,
        "is_completed": is_completed,
        "content": content,
        "created_at": f"{created_at}T",
        "creator_id": None,
        "description": None,
        "id": None,
        "priority": priority,
        "project_id": project_id,
        "section_id": section_id,
        "url": None,
        "labels": labels,
        "due": due
    })
    

def make_new_test_case(migration, todoist_task, todoist_project):
    todoist_project.id = 1
    todoist_task.project_id = todoist_project.id

    migration.get_project_by_id_map = lambda: {todoist_project.id: todoist_project}

    return migration

def make_project_map(migration, projects):
    m = {}
    for p in projects:
        m[p.id] = p
    migration.get_project_by_id_map = lambda: m
    return m

def make_section_map(migration, sections):
    m = {}
    for p in sections:
        m[p.id] = p
    migration.get_section_by_id_map = lambda: m
    return m


@pytest.fixture
def migration():
    m = Migration(token=None, keep_todoist_id=False)
    m.get_project_by_id_map = lambda: {}
    return m

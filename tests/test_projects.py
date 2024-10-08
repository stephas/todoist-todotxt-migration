from utils import make_todoist_task, make_todoist_project, make_new_test_case, make_project_map, migration

from todoist_todotxt_migration.tools import Migration, ProjectRenameStrategy
from todoist_api_python.models import Task, Project

# TBD: test creation date missing

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


def test_project_with_parents(migration):
    p = make_todoist_project("A project", id=1, parent_id=2)
    pp = make_todoist_project("A parent project", id=2)

    assert 3 not in make_project_map(migration, [p, pp])
    assert 2 in migration.get_project_by_id_map()

    t = make_todoist_task("A task", priority=1, project_id=1)

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase)
    assert todotxt_task == "2022-12-20 A task +AProject +AParentProject"

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase, project_strategy='Folder')
    assert todotxt_task == "2022-12-20 A task +AParentProject/AProject +AParentProject"

    #todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase, project_strategy='AncestorContext')
    #assert todotxt_task == "2022-12-20 A task @AProject +AParentProject"


    ppp = make_todoist_project("A grandparent project", id=3)
    pp.parent_id = 3
    assert 3 in make_project_map(migration, [p, pp, ppp])

    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase, project_strategy='Names')
    assert todotxt_task == "2022-12-20 A task +AProject +AParentProject +AGrandparentProject"
    todotxt_task = migration.transform_task(t, rename_strategy=ProjectRenameStrategy.Uppercase, project_strategy='Folder')
    assert todotxt_task == "2022-12-20 A task +AGrandparentProject/AParentProject/AProject +AGrandparentProject/AParentProject +AGrandparentProject"
    #assert todotxt_task == "2022-12-20 A task @AProject +AGrandparentProject/AParentProject +AGrandparentProject"

    # should the context be the grandparents and parents? or should it be the project iself? should it be a choice

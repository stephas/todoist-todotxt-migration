from utils import make_todoist_task, make_todoist_project, make_new_test_case, make_project_map, migration

# TBD: should a rename strategy be used for labels too?
# a todoist label doesn't have spaces, if used they replace them with underscores

def test_task_labels(migration):
    t = make_todoist_task("A task", priority=1, labels=["label", "another_label", "Ok"])

    todotxt_task = migration.transform_task(t)

    assert todotxt_task == "2022-12-20 A task @label @another_label @Ok"

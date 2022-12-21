from utils import make_todoist_task, make_todoist_project, make_new_test_case, make_project_map, make_todoist_section, make_section_map, migration

# todoist sections are imported like labels are, with the difference of applying the naming strategy because they can contain spaces and todotxt can't

def test_task_contexts(migration):
    # not used
    s1 = make_todoist_section("A section", id=10)
    # used
    s2 = make_todoist_section("another section", id=11)
    make_section_map(migration, [s1, s2])

    p = make_todoist_project("A project", id=20)
    make_project_map(migration, [p])

    t = make_todoist_task("A task", priority=1, labels=["label"], project_id=20, section_id=11)

    todotxt_task = migration.transform_task(t)

    assert todotxt_task == "2022-12-20 A task +AProject @anotherSection @label"

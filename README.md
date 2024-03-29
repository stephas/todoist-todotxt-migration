# todoist-todotxt-migration

```
export TODOIST_TOKEN="your api token here from todoist: open profile -> integrations -> developer -> API token"
```
Usage:

```python
def migrate():
    print('--- migrate ----')
    migration = Migration.from_env_secret(keep_todoist_id=True)
    migration.generate_file(path='/usr/src/app/todo')
    migration.clear_cache()

def remove_completed_todotxt_from_todoist():
    print('--- remove completed todotxt from todoist ----')
    migration = Migration.from_env_secret(keep_todoist_id=True)
    migration.complete_todoist_tasks_from_todotxt(path='/usr/src/app/todo')
    migration.clear_cache()
```

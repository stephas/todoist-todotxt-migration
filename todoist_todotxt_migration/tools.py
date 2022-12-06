import os
from functools import lru_cache

from todoist_api_python.api import TodoistAPI

class Migration:
    @staticmethod
    def from_env_secret():
        token = os.getenv('TODOIST_TOKEN')
        assert token
        return Migration(token)

    def __init__(self, token):
        self.api = TodoistAPI(token)

    @lru_cache
    def get_project_by_id_map(self):
        projects = self.api.get_projects()
        project_by_id = {}
        for p in projects:
            project_by_id[p.id] = p
        return project_by_id

    @lru_cache
    def get_tasks(self):
        return self.api.get_tasks()
    
    def clear_cache(self):
        self.get_project_by_id_map.cache_clear()
        self.get_tasks.cache_clear()

    def generate_file(self, filename='todo.txt', path='.'):
        fullpath = os.path.join(path, filename)
        print(f"generating file {fullpath}")
        # write to todo.txt
        with open(fullpath, 'w') as fh:
            for t in self.get_tasks():
                fh.write(self.transform_task(t) + '\n')

    def transform_task(self, t):
        project_by_id = self.get_project_by_id_map()

        # is_completed
        is_completed = 'x ' if t.is_completed else ""
        # priority
        priority = {1: '', 2: '(C) ', 3: '(B) ', 4: '(A) '}[t.priority]
        # completion_date
        # creation date (needed if completion date is there) TBD
        created_at = t.created_at.split('T')[0] + " "
        # +projecttag TBD find children as option
        project_transform = " +" + project_by_id[t.project_id].name.replace(' ', '_') if t.project_id else ""
        # @context tag
        labels = " @" + " @".join(t.labels) if t.labels else ""
        # special key value due:2016-05-30
        due = " due:" + t.due.date if t.due else ""
        rec = " rec:1d" if t.due and t.due.string == "every day" else ""
        if t.is_completed:
            print(t)
            assert False
            print(True)
        return is_completed + priority + created_at + t.content + project_transform + labels + due + rec
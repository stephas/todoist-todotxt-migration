import os
from functools import lru_cache

from todoist_api_python.api import TodoistAPI


class ProjectRenameStrategy:
    @staticmethod
    def Uppercase(todoist_project):
        project_words = todoist_project.name.split()
        uppercase_tail_words = [w[0].upper()+w[1:] for w in project_words[1:]]
        return "".join([project_words[0]] + uppercase_tail_words)

    @staticmethod
    def UppercaseAll(todoist_project):
        project_words = todoist_project.name.split()
        uppercase_words = [w[0].upper()+w[1:] for w in project_words]
        return "".join(uppercase_words)

    @staticmethod
    def Underscore(todoist_project):
        return todoist_project.name.replace(' ', '_')


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

    # TBD: get project with sections by id dict

    @lru_cache
    def get_section_by_id_map(self):
        sections = self.api.get_sections()
        section_by_id = {}
        for p in sections:
            section_by_id[p.id] = p
        return section_by_id

    @lru_cache
    def get_tasks(self):
        return self.api.get_tasks()
    
    def clear_cache(self):
        self.get_project_by_id_map.cache_clear()
        self.get_section_by_id_map.cache_clear()
        self.get_tasks.cache_clear()

    def generate_file(self, filename='todo.txt', path='.'):
        fullpath = os.path.join(path, filename)
        print(f"generating file {fullpath}")
        # write to todo.txt
        with open(fullpath, 'w') as fh:
            for t in self.get_tasks():
                fh.write(self.transform_task(t) + '\n')

    def projects_with_ancestors(self, project_id):
        project = self.get_project_by_id_map()[project_id]
        projects = [project]

        if project.parent_id:
            projects += self.projects_with_ancestors(project.parent_id)

        return projects


    def todotxt_project_for_todoist_task(self, t, rename_strategy, parent_strategy):
        todotxt_project = ""

        if t.project_id:
            projects = self.projects_with_ancestors(t.project_id)

            def Folder(projects):
                project_folders = []
                for i, p in enumerate(projects):
                    projects_for_path = projects[i:]
                    project_folder = "/".join(reversed([rename_strategy(pp) for pp in projects_for_path]))
                    project_folders.append(project_folder)

                transform = " +".join([p for p in project_folders])
                return " +" + transform

            def Names(projects):
                transform = " +".join([rename_strategy(p) for p in projects])
                return " +" + transform

            if parent_strategy == 'Folder':
                todotxt_project = Folder(projects)
            elif parent_strategy == 'tbd':
                todotxt_project = Names(projects)
            else:
                todotxt_project = Names(projects)


        return todotxt_project


    def todotxt_context_for_todoist_section(self, t, rename_strategy):
        todotxt_section = ""

        if t.section_id:
            section = self.get_section_by_id_map()[t.section_id]
            todotxt_section = " @" + rename_strategy(section)

        return todotxt_section


    def transform_task(self, t, rename_strategy=ProjectRenameStrategy.Uppercase, project_strategy='Names'):
        # is_completed
        is_completed = 'x ' if t.is_completed else ""
        # priority
        priority = {1: '', 2: '(C) ', 3: '(B) ', 4: '(A) '}[t.priority]
        # completion_date
        # creation date (needed if completion date is there) TBD
        created_at = t.created_at.split('T')[0] + " "
        # +projecttag TBD find children as option
        project_transform = self.todotxt_project_for_todoist_task(t, rename_strategy, project_strategy)
        contexts = self.todotxt_context_for_todoist_section(t, rename_strategy)
        # @context tag
        labels = " @" + " @".join(t.labels) if t.labels else ""
        # special key value due:2016-05-30
        due = " due:" + t.due.date if t.due else ""
        rec = " rec:1d" if t.due and t.due.string == "every day" else ""

        if t.is_completed:
            print(t)
            assert False
            # TBD
            print(True)

        return is_completed + \
                priority + \
                created_at + \
                t.content + \
                project_transform + \
                contexts + labels + \
                due + \
                rec

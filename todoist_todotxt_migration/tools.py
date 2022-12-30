import os
import re

from datetime import date, timedelta
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
    def from_env_secret(keep_todoist_id=False):
        token = os.getenv('TODOIST_TOKEN')
        assert token
        return Migration(token, keep_todoist_id=keep_todoist_id)

    def __init__(self, token, keep_todoist_id):
        self.api = TodoistAPI(token)
        self.config_keep_todoist_id = keep_todoist_id

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

    def complete_todoist_tasks_from_todotxt(self, filename='todo.txt', path='.'):
        fullpath = os.path.join(path, filename)
        # read from todo.txt
        tasks = []
        with open(fullpath, 'r') as fh:
            tasks = [t.strip() for t in fh.readlines()]

        done_tasks = [t for t in tasks if t.startswith("x ")]
        for t in done_tasks:
            todoist_id_search = re.search(r'todoist:(\d+)', t)
            if todoist_id_search:
                todoist_id = todoist_id_search.group(1)
                self.api.close_task(task_id=todoist_id)
                print(f"completed {todoist_id}")

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


    def todotxt_due_for_todoist_due(self, t):
        todotxt_due = ""

        if t.due:
            todotxt_due = " due:" + t.due.date

            if t.due.is_recurring:
                create_date = date.fromisoformat(t.created_at.split('T')[0])
                due_date = date.fromisoformat(t.due.date)

                if due_date < create_date:
                    raise NotImplementedError("due date before create date is not understood")

                due_string = t.due.string.lower().strip()

                rec_value = None

                print(due_string)
                lys = re.match(r'(bi)?([dwmy])(?:ai|eek|onth|ear)ly', due_string)
                every = re.match(r'every\s+(day|week|month|year)', due_string)
                every_nth = re.match(r'every\s+(other|\d+)\s+([dwmy])', due_string)

                # shortest string to uniquely identify  all months and weekdays:
                #'th,tu,o,d,ap,au,mar,may,mo,w,sa,se,su,fe,fr,no,ja,jun,jul'
                #weekday_or_month = re.match(r'every\s+(other\s+)?(th|tu|o|d|ap|au|mar|may|mo|w|sa|se|su|fe|fr|no|ja|jun|jul)', due_string)
                weekday = re.match(r'every\s+(other\s+)?(th|tu|mo|w|sa|su|fr)', due_string)
                explicit_day_of_month_or_year = re.match(r'every\s+(other\s+)?(\d+)?(?:st|nd|rd|th)?\s*(o|d|ap|au|mar|may|se|fe|no|ja|jun|jul)?(?:\w*\s+(\d+)?(?:st|nd|rd|th)?)?', due_string)
                if explicit_day_of_month_or_year:
                    print(explicit_day_of_month_or_year.groups())

                if lys:
                    double, time_span = lys.groups()
                    rec_value = ('2' if double else '') + time_span
                elif every:
                    rec_value = every.group(1)[0]
                elif every_nth:
                    count, timespan = every_nth.groups()

                    if count == "other":
                        count = "2"

                    rec_value = count + timespan
                elif weekday:
                    double_time = weekday.group(1)
                    found_name = weekday.group(2)

                    weekdays = "mo,tu,w,th,fr,sa,su".split(',')
                    weekday_as_number_from_every_string = [n for n,letters in enumerate(weekdays) if found_name.startswith(letters)][0]
                    weekday_from_due = due_date.weekday()
                    day_difference = (weekday_from_due - weekday_as_number_from_every_string)
                    day_difference = (day_difference + 7) % 7

                    new_due = due_date - timedelta(days=day_difference)


                    # moving it backwards to make it overdue but keep the strict weekly occurence
                    if double_time:
                        date_diff = due_date - create_date
                        if (date_diff.days % 14) >= 7:
                            new_due = new_due - timedelta(days=7)

                    todotxt_due = f" due:{new_due}"
                    rec_value = "+2w" if double_time else '+1w'

                elif explicit_day_of_month_or_year:
                    double_time, prefix_day, month_token, postfix_day = explicit_day_of_month_or_year.groups()
                    found_explicit_day = int(prefix_day or postfix_day or 0) or False

                    time_span = "y" if month_token else "m"
                    double_span = "+2" if double_time else '+1'

                    if found_explicit_day:
                        if found_explicit_day == due_date.day:
                            rec_value = double_span + time_span
                        else:
                            rec_value = "tbd"
                            raise NotImplementedError(t.due.date, due_string, found_explicit_day, due_date.day, "due date day doesn't align")
                    else:
                        months = "ja|fe|mar|ap|may|jun|jul|au|se|o|no|d".split('|')
                        month_as_number_from_every_string = [n+1 for n,letters in enumerate(months) if month_token.startswith(letters)][0]
                        if month_as_number_from_every_string != due_date.month:
                            raise NotImplementedError(t.due.date, due_string, found_explicit_day, due_date.day, "due date month doesn't align")

                        rec_value = double_span + time_span


                    new_due = due_date
                    # moving it backwards to make it overdue but keep the strict yearly occurence
                    if double_time:
                        year_diff = due_date.year - create_date.year
                        if (year_diff % 2 >= 1):
                            print("shift year")
                            #new_due = new_due - timedelta(days=365)
                            new_due = date(new_due.year - 1, new_due.month, new_due.day)

                    todotxt_due = f" due:{new_due}"

                else:
                    rec_value = "err"
                    raise NotImplementedError(t.due.date, due_string)

                todotxt_due += f" rec:{rec_value}"

        return todotxt_due


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
        due = self.todotxt_due_for_todoist_due(t)

        todoist_id = f" todoist:{t.id}" if self.config_keep_todoist_id else ""

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
                todoist_id

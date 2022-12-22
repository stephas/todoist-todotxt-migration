import pytest

from utils import make_todoist_task, make_todoist_due, migration

# Note: strict recurrance (+) is based on the due date, as opposed to the completion date (birthday vs water plants)

# based on completion date, non-strict, no +
# -----------------------
# daily, weekly, monthly yearly
# every (other) day, week, month, year
# every x days, weeks, months, years

# strict mode
# -----
# every (1-13) st/nd/rd/th (default of month, month of year)  (and flipped)
# every (other) nameofday or name of month (find set)

# fail on not understanding recurrance

@pytest.fixture
def due_task(migration):
    def make_due_task(recurring_string="", due_date="2022-12-22"):
        t = make_todoist_task("A task", due=make_todoist_due(due_date, string=recurring_string))
        return migration.transform_task(t)
    return make_due_task


def test_not_recurring(migration, due_task):
    assert due_task() == "2022-12-20 A task due:2022-12-22"


# (based on completion date) every x days, weeks, months, years
def test_every_x_days_weeks_months_years(migration, due_task):
    assert due_task("every 1 days")   == "2022-12-20 A task due:2022-12-22 rec:1d"
    assert due_task("every 1 day")    == "2022-12-20 A task due:2022-12-22 rec:1d"
    assert due_task("every 3 days")   == "2022-12-20 A task due:2022-12-22 rec:3d"
    assert due_task("Every 7 Days")   == "2022-12-20 A task due:2022-12-22 rec:7d"
    assert due_task("Every 1 Week")   == "2022-12-20 A task due:2022-12-22 rec:1w"
    assert due_task("Every 5 months") == "2022-12-20 A task due:2022-12-22 rec:5m"
    assert due_task("Every 7 years")  == "2022-12-20 A task due:2022-12-22 rec:7y"

# daily, weekly, monthly yearly
# every (other) day, week, month, year
def test_timeperiod_lys(migration, due_task):
    assert due_task("daily")   == "2022-12-20 A task due:2022-12-22 rec:d"
    assert due_task("weekly")  == "2022-12-20 A task due:2022-12-22 rec:w"
    assert due_task("monthly") == "2022-12-20 A task due:2022-12-22 rec:m"
    assert due_task("yearly")  == "2022-12-20 A task due:2022-12-22 rec:y"
    #with pytest.raises(NotImplementedError):
    #    assert due_task("hourly")

def test_every_other(migration, due_task):
    assert due_task("every day")   == "2022-12-20 A task due:2022-12-22 rec:d"
    assert due_task("every week")   == "2022-12-20 A task due:2022-12-22 rec:w"
    assert due_task("every month")   == "2022-12-20 A task due:2022-12-22 rec:m"
    assert due_task("every year")   == "2022-12-20 A task due:2022-12-22 rec:y"
    assert due_task("every other day")   == "2022-12-20 A task due:2022-12-22 rec:2d"
    assert due_task("every other week")   == "2022-12-20 A task due:2022-12-22 rec:2w"
    assert due_task("every other month")   == "2022-12-20 A task due:2022-12-22 rec:2m"
    assert due_task("every other year")   == "2022-12-20 A task due:2022-12-22 rec:2y"

# strict ------
def test_weekday(migration, due_task):
    assert due_task("every mon", "2022-12-26")   == "2022-12-20 A task due:2022-12-26 rec:+1w"
    # todo.txt can't express this scenary exactly (afaik), the task was presumably moved forward
    # but repeats weekly on a different day, let's make it overdue and +1w,
    # which should practicly be the same, but in case of ambiguity will make user move it
    assert due_task("every sat", "2022-12-26")   == "2022-12-20 A task due:2022-12-24 rec:+1w"
    assert due_task("every tues", "2022-12-27")   == "2022-12-20 A task due:2022-12-27 rec:+1w"
    assert due_task("every Sunday", "2022-12-25")   == "2022-12-20 A task due:2022-12-25 rec:+1w"
    assert due_task("every other fri", "2022-12-23")   == "2022-12-20 A task due:2022-12-23 rec:+2w"
    #TBD test case with other like for sat

# every (1-13) st/nd/rd/th (default of month, month of year)  (and flipped)
def test_every_nth_of_month(migration, due_task):
    assert due_task("every 20th", "2022-12-20")   == "2022-12-20 A task due:2022-12-20 rec:+1m"
#    assert due_task("every 21st")   == "2022-12-20 A task due:2022-12-22 rec:m"
#    assert due_task("every 22nd")   == "2022-12-20 A task due:2022-12-22 rec:m"
#    assert due_task("every 23rd")   == "2022-12-20 A task due:2022-12-22 rec:m"

import pytest

from utils import make_todoist_task, make_todoist_due, migration

# Note: strict recurrance (+) is based on the due date, as opposed to the completion date (birthday vs water plants)

# daily, weekly, monthly yearly
# every (other) day, week, month, year
#   The two formats above will convert to:
# (based on completion date, non-strict, no +) every x days, weeks, months, years

# every (other) nameofday or name of month (find set)

# every (1-13) st/nd/rd/th (default of month, month of year)  (and flipped)

# fail on not understanding recurrance

@pytest.fixture
def due_task(migration):
    def make_due_task(recurring_string=""):
        t = make_todoist_task("A task", due=make_todoist_due("2022-12-22", string=recurring_string))
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
    with pytest.raises(NotImplementedError):
        assert due_task("hourly")

def test_every_other(migration, due_task):
    assert due_task("every other day")   == "2022-12-20 A task due:2022-12-22 rec:2d"
    assert due_task("every other year")   == "2022-12-20 A task due:2022-12-22 rec:2y"

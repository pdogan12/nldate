from datetime import date
from nldate import parse

#
def test_today():
    d = date(2025, 6, 1)
    assert parse("today", today=d) == d

def test_tomorrow():
    d = date(2025, 6, 1)
    assert parse("tomorrow", today=d) == date(2025, 6, 2)

def test_yesterday():
    d = date(2025, 6, 1)
    assert parse("yesterday", today=d) == date(2025, 5, 31)

#
def test_in_n_days():
    d = date(2025, 6, 1)
    assert parse("in 5 days", today=d) == date(2025, 6, 6)

def test_n_days_from_now():
    d = date(2025, 6, 1)
    assert parse("3 days from now", today=d) == date(2025, 6, 4)

def test_n_weeks_from_now():
    d = date(2025, 6, 1)
    assert parse("in 2 weeks", today=d) == date(2025, 6, 15)

# 
def test_next_tuesday():
    d = date(2025, 6, 1)  
    assert parse("next Tuesday", today=d) == date(2025, 6, 3)

def test_last_friday():
    d = date(2025, 6, 1) 
    assert parse("last Friday", today=d) == date(2025, 5, 30)

# 
def test_absolute_date():
    assert parse("December 1st, 2025") == date(2025, 12, 1)

def test_absolute_date_no_suffix():
    assert parse("January 15 2026") == date(2026, 1, 15)

#
def test_days_before_absolute():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)

def test_days_after_relative():
    d = date(2025, 6, 1)
    assert parse("2 weeks from tomorrow", today=d) == date(2025, 6, 16)
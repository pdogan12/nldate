import re
from datetime import date, timedelta

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

WORD_TO_NUM = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _to_int(s: str) -> int:
    s = s.strip()
    if s.isdigit():
        return int(s)
    return WORD_TO_NUM.get(s.lower(), 0)


def _parse_base(s: str, today: date) -> date:
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)
    return _try_absolute(s) or today


def _try_absolute(s: str) -> date | None:
    pattern = r"(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})"
    m = re.fullmatch(pattern, s.strip(), re.IGNORECASE)
    if m:
        month = MONTHS.get(m.group(1).lower())
        day = int(m.group(2))
        year = int(m.group(3))
        if month:
            return date(year, month, day)
    # "2025-12-01"
    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s.strip())
    if iso:
        return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))

    # "2025/12/04"
    slash = re.fullmatch(r"(\d{4})/(\d{2})/(\d{2})", s.strip())
    if slash:
        return date(int(slash.group(1)), int(slash.group(2)), int(slash.group(3)))
    return None


def _try_keywords(s: str, today: date) -> date | None:
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)
    return None


def _try_relative(s: str, today: date) -> date | None:
    # "in 5 days", "in 2 weeks", "in 1 year"
    m = re.fullmatch(r"in (\w+) (days?|weeks?|months?|years?)", s, re.IGNORECASE)
    if m:
        n = _to_int(m.group(1))
        unit = m.group(2).lower().rstrip("s")
        return _apply_offset(today, n, unit)
    # "3 days from now"
    m = re.fullmatch(r"(\w+) (days?|weeks?|months?|years?) from now", s, re.IGNORECASE)
    if m:
        n = _to_int(m.group(1))
        unit = m.group(2).lower().rstrip("s")
        return _apply_offset(today, n, unit)
    return None


def _try_next_last_weekday(s: str, today: date) -> date | None:
    m = re.fullmatch(r"(next|last) (\w+)", s, re.IGNORECASE)
    if not m:
        return None
    direction = m.group(1).lower()
    weekday_str = m.group(2).lower()
    if weekday_str not in WEEKDAYS:
        return None
    target = WEEKDAYS.index(weekday_str)
    current = today.weekday()
    if direction == "next":
        delta = (target - current) % 7
        if delta == 0:
            delta = 7
    else:
        delta = (current - target) % 7
        if delta == 0:
            delta = 7
        delta = -delta
    return today + timedelta(days=delta)


def _try_offset_from_base(s: str, today: date) -> date | None:
    m = re.fullmatch(
        r"(\w+) (days?|weeks?|months?|years?) (before|after|from) (.+)",
        s,
        re.IGNORECASE,
    )
    if m:
        n = _to_int(m.group(1))
        unit = m.group(2).lower().rstrip("s")
        direction = m.group(3).lower()
        base = _parse_base(m.group(4).strip(), today)
        if direction == "before":
            return _apply_offset(base, -n, unit)
        else:
            return _apply_offset(base, n, unit)
    return None


def _apply_offset(base: date, n: int, unit: str) -> date:
    unit = unit.rstrip("s")
    if unit == "day":
        return base + timedelta(days=n)
    if unit == "week":
        return base + timedelta(weeks=n)
    if unit == "month":
        month = base.month - 1 + n
        year = base.year + month // 12
        month = month % 12 + 1
        return date(year, month, base.day)
    if unit == "year":
        return date(base.year + n, base.month, base.day)
    return base


def parse(s: str, today: date | None = None) -> date:
    today = today or date.today()
    s = s.strip()
    sl = s.lower()

    if result := _try_keywords(sl, today):
        return result
    if result := _try_relative(sl, today):
        return result
    if result := _try_next_last_weekday(sl, today):
        return result
    if result := _try_offset_from_base(sl, today):
        return result
    if result := _try_absolute(sl):
        return result

    raise ValueError(f"Cannot parse date: {s!r}")

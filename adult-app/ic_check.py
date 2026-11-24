"""
ic_check.py - checks that a Malaysian IC (MyKad / MyKid) number looks real.

PRIVACY: an IC number is sensitive personal data (Malaysia's PDPA).
This prototype only checks that the number has 12 digits and starts
with a real birth date (YYMMDD). Then it forgets the IC. NOTHING from
the IC is saved: not the number, not the birth date, not an age group.

Demo only: please use made-up IC numbers.
"""

import datetime


def clean_ic(text):
    """Remove dashes and spaces: '150301-10-1234' -> '150301101234'."""
    return text.replace("-", "").replace(" ", "").strip()


def check_ic(text, today=None):
    """
    Returns None when the IC looks valid, else a friendly sentence
    saying what is wrong.
    """
    today = today or datetime.date.today()
    ic = clean_ic(text)

    if len(ic) != 12 or not ic.isdigit():
        return "An IC number has 12 digits, like 150301-10-1234."

    # The first 6 digits are the birth date: YY MM DD.
    yy = int(ic[0:2])
    mm = int(ic[2:4])
    dd = int(ic[4:6])

    # The IC only has 2 digits for the year. If they are bigger than this
    # year's 2 digits, the person was born in the 1900s.
    if yy <= today.year % 100:
        year = 2000 + yy
    else:
        year = 1900 + yy

    try:
        birth = datetime.date(year, mm, dd)
    except ValueError:
        return "The first 6 digits should be a birth date (YYMMDD)."

    if birth > today:
        return "The birth date in this IC is in the future."
    return None


# Quick self-test: run `python ic_check.py`
if __name__ == "__main__":
    day = datetime.date(2026, 11, 21)
    assert check_ic("150301-10-1234", day) is None
    assert check_ic("900101-14-5678", day) is None
    assert check_ic("12345", day) is not None
    assert check_ic("151301-10-1234", day) is not None       # month 13
    assert check_ic("261122-10-1234", day) is not None       # tomorrow
    assert check_ic("abcdefghijkl", day) is not None
    print("All IC checks passed.")

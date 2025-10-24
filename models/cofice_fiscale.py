import datetime
_ODD_MAP = {
    **dict.fromkeys(list("0"), 1), **dict.fromkeys(list("1"), 0), **dict.fromkeys(list("2"), 5),
    **dict.fromkeys(list("3"), 7), **dict.fromkeys(list("4"), 9), **dict.fromkeys(list("5"), 13),
    **dict.fromkeys(list("6"), 15), **dict.fromkeys(list("7"), 17), **dict.fromkeys(list("8"), 19),
    **dict.fromkeys(list("9"), 21),
    **dict.fromkeys(list("A"), 1), **dict.fromkeys(list("B"), 0), **dict.fromkeys(list("C"), 5),
    **dict.fromkeys(list("D"), 7), **dict.fromkeys(list("E"), 9), **dict.fromkeys(list("F"), 13),
    **dict.fromkeys(list("G"), 15), **dict.fromkeys(list("H"), 17), **dict.fromkeys(list("I"), 19),
    **dict.fromkeys(list("J"), 21), **dict.fromkeys(list("K"), 2), **dict.fromkeys(list("L"), 4),
    **dict.fromkeys(list("M"), 18), **dict.fromkeys(list("N"), 20), **dict.fromkeys(list("O"), 11),
    **dict.fromkeys(list("P"), 3), **dict.fromkeys(list("Q"), 6), **dict.fromkeys(list("R"), 8),
    **dict.fromkeys(list("S"), 12), **dict.fromkeys(list("T"), 14), **dict.fromkeys(list("U"), 16),
    **dict.fromkeys(list("V"), 10), **dict.fromkeys(list("W"), 22), **dict.fromkeys(list("X"), 25),
    **dict.fromkeys(list("Y"), 24), **dict.fromkeys(list("Z"), 23),
}

_EVEN_MAP = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}

_CHECK_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_MONTH_CODES = {
    1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "H",
    7: "L", 8: "M", 9: "P", 10: "R", 11: "S", 12: "T"
}

def _extract_chars(s, consonants_only=False):
    s = s.upper()
    consonants = [c for c in s if c.isalpha() and c not in "AEIOU"]
    vowels = [c for c in s if c.isalpha() and c in "AEIOU"]
    chars = consonants if consonants_only else (consonants + vowels)
    chars += ["X"] * (3 - len(chars))
    return "".join(chars[:3])

def _code_surname(surname):
    return _extract_chars(surname)

def _code_name(name):
    name = name.upper()
    consonants = [c for c in name if c.isalpha() and c not in "AEIOU"]
    if len(consonants) >= 4:
        chars = [consonants[i] for i in (0, 2, 3)]
    else:
        chars = consonants
    vowels = [c for c in name if c in "AEIOU"]
    chars += vowels
    chars += ["X"] * (3 - len(chars))
    return "".join(chars[:3])

def _code_date_gender(date_str, gender):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    year = d.year % 100
    month = _MONTH_CODES[d.month]
    day = d.day + (40 if gender.upper() == "F" else 0)
    return f"{year:02d}{month}{day:02d}"

def _compute_control(cf15):
    total = 0
    for i, c in enumerate(cf15):
        if (i + 1) % 2 == 1:
            total += _ODD_MAP[c]
        else:
            total += _EVEN_MAP[c]
    return _CHECK_CHARS[total % 26]

def generate_codice_fiscale(surname, name, date_of_birth, gender, comune_code):
    part1 = _code_surname(surname)
    part2 = _code_name(name)
    part3 = _code_date_gender(date_of_birth, gender)
    cf15 = part1 + part2 + part3 + comune_code.upper()
    control = _compute_control(cf15)
    return cf15 + control

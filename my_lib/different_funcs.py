def printf(*args, sep: str = ' ', end: str = '\n', col: int = 197, bg: int = 0):
    str = ''

    for arg in args:
        str += f'{sep}{arg}'

    print(f"\033[38;5;{col}m\033[48;5;{bg}m{str}\033[0m", end=end)


def console_clear():
    print('\033[2J')


def conv_to_pref_format(seconds):
    days = seconds // (24 * 3600)

    seconds = seconds % (24 * 3600)
    hours = int(seconds // 3600)

    seconds %= 3600
    minutes = int(seconds // 60)

    seconds %= 60

    return (days, hours, minutes, seconds)


def get_hours_ending(hours):
    ending = ''

    number = hours % 20

    if number == 1:
        ending = 'час'

    elif number > 1 and number < 5:
        ending = 'часа'

    else:
        ending = 'часов'

    return ending


def convert_list_to_string(lst=None):
    if lst:
        string = ''

        for item in lst:
            string += f'{item},'

        return string[:-1]


def convert_cyrillic_letters_to_latin(string):
    transcript_symbols = [
        'a', 'b', 'v', 'g', 'd', 'e', 'zh', 'z',
        'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r',
        's', 't', 'u', 'f', 'h', 'c', 'ch', 'sh',
        'shch', '', 'y', '', 'e', 'yu', 'ya'
    ]

    start_index = ord('а')
    slug = ''

    for char in string.lower():
        if 'в' <= char <= 'я':
            slug += transcript_symbols[ord(char) - start_index]
        elif char == 'ё':
            slug += 'yo'
        # elif char in ' !?;:.,':
        #     slug += '-'
        else:
            slug += char

    while '--' in slug:
        slug = slug.replace('--', '-')

    return slug

    # Данный функционал реализовать используя регулярные выражения

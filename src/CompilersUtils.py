
def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def coloredDef(text):
    return colored(255, 0, 0, text)


def first(items: list, predicate: callable):
    """
    Find the first occurrence in items that satisfies te given predicate.
    :param items: The list to search
    :param predicate: The predicate that must be satisfied
    :return: The first match if found, else None
    """
    return next((item for item in items if predicate(item)), None)

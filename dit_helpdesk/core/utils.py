def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa: E203


def unique(iterable):
    seen = set()
    for i in iterable:
        if i in seen:
            continue
        seen.add(i)
        yield i

def sort_by(field, articles, reverse=False):
    return sorted(articles, reverse=reverse, key=lambda p: p[field])


def log(mess_type, message):
    print('%s: %s' % (mess_type, message))

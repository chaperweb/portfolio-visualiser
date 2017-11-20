from django import template
import datetime
register = template.Library()

def print_timestamp(timestamp):
    try:
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y")

register.filter(print_timestamp)

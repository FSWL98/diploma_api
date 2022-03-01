import re

def is_valid_email(email):
    regex = '^[^\s@]+@([^\s@.,]+\.)+[^\s@.,]{2,}$'
    return re.search(regex, email)

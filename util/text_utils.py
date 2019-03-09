import re

def an_finder(text):
    pattern = re.compile(' an an ')
    result = pattern.search(text)
    return result.group()

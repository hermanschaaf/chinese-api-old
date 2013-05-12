import re

re_allowed_domains = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
re_valid_key = re.compile(r"^([A-Z\d][A-Z\d-]+[A-Z\d])$", re.IGNORECASE)

def is_valid_key(key):
    """
    >>> is_valid_key('chineselevel')
    True
    >>> is_valid_key('test-key')
    True
    >>> is_valid_key('notvalid-')
    False
    >>> is_valid_key('not valid')
    False
    >>> is_valid_key('also.notvalid')
    False
    """
    return all([re_valid_key.match(key)])

def is_valid_domain(hostname):
    """
    Tests whether a string is a valid domain name for the purposes
    of our API.

    >>> is_valid_domain('test.com')
    True
    >>> is_valid_domain('www.test.com')
    True
    >>> is_valid_domain('http://test.com')
    False
    >>> is_valid_domain('test.com:5000')
    True
    >>> is_valid_domain('local.dev')
    True
    >>> is_valid_domain('test.com:512321')
    False
    >>> is_valid_domain('test.com:512-3')
    False
    >>> is_valid_domain('hello')
    False
    >>> is_valid_domain('hello.co.za')
    True
    >>> is_valid_domain('localhost')
    True
    >>> is_valid_domain('127.0.0.1')
    True
    """
    if len(hostname) > 255:
        return False
    if hostname[-1:] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    if hostname.find(':') >= 0: 
        port = hostname[hostname.rfind(':')+1:]
        allowed_port = re.compile("^([\d]{1,5})$")
        if not allowed_port.match(port):
            return False
        hostname = hostname[:hostname.rfind(':')]

    if hostname == 'localhost': # special case for localhost
        return True
    if not len(hostname.split(".")) >= 2:
        return False
    return all(re_allowed_domains.match(x) for x in hostname.split("."))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
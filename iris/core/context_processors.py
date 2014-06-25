"""
Context processors which accept one argument of HTTPRequest
and return a dict that can be used in all templates.
"""
from iris import VERSION


def version(request):
    """
    Returns IRIS version in tuple
    """
    return {'version': VERSION}

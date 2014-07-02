"""
Context processors which accept one argument of HTTPRequest
and return a dict that can be used in all templates.
"""
import pkg_resources

# pylint: disable=E1103
# E1103: version: Instance of 'str' has no 'version' member


def version(_request):
    """
    Returns IRIS version in tuple
    """
    try:
        ver = pkg_resources.get_distribution('iris').version
    except pkg_resources.DistributionNotFound:
        ver = 'dev'
    return {'version': ver}

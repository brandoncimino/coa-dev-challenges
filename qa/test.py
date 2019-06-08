import pytest
from validate_url import *

# Demonstrate how the use pytest
def example_func(x):
    return x + 1

def test_example_failure():
    assert example_func(3) == 5

def test_example_success():
    assert example_func(1) == 2

# Example with our function
def test_identity():
    assert validate_url("www.austintexas.gov") == "www.austintexas.gov"

# Write your own tests below
# The names of your functions must be prefixed with "test_" in order for pytest to pick them up.

# -------------------------
# -- Brandon's Functions --
# -------------------------

# Takes in a URL and outputs a list of all the parameters in it.
def get_params(url):
    pat = r'(?P<param>[^?&=]*?)=(?P<value>[^&=$]*)'
    return re.findall(pat,url,re.IGNORECASE)

# Takes in a list of parameters, and returns the "expected" parameters that should be in a validated URL.
# The parameter list returned should:
#   - Maintain the order of the original parameters
#   - Include each parameter only once
#   - Include the first (left-most) value for each parameter (when the parameter appears more than once)
#   - Exclude any parameters in the optional "excluded" array
def get_expected_params(params,excluded=[]):
    px = []
    for p in params:
        if p[0].lower() not in [i[0].lower() for i in px] and p[0].lower() not in [e.lower() for e in excluded]:
            px.append(p)

    return px

# Takes in a URL and returns regex match information about the domains.
# There are two named capture groups returned. For the URL "https://www.austin.texas.gov":
#   - "top": the top-level domain, i.e. ".gov"
#   - "lower": ALL non-top level domains, as a single string, i.e. "www.austin.texas"
def get_domains(url):
    pat = r'(https?://)?(?P<lower>.+)(?P<top>\.[a-zA-Z\d-]+)'
    return re.match(pat,url)

# Takes in a URL and an optional list of parameter exclusions, then validates it using "validate_url" and returns whether or not that validation was successful.
# NOTE: This test contains multiple assertions. If an assertion fails, subsequent assertions will not be executed.
#   - This causes test executions to be quicker, but also less verbose.
#   - One option to increase verbosity would be to split assertions up into their own methods, then create a parameterized test that takes in a method, then pass an array of the assertion methods to that parameterized test.
#   - The above solution would benefit from separating out individual test requirements, which may or may not be desired. For example, one assertion currently checks for duplicate parameters and excluded parameters - ideally those would be split.
#   - The above solution was definitely overkill for this exercise, but I could provide a proof-of-concept if desired.
@pytest.mark.parametrize(
    ['url_before','excluded'],
    [
        #REQ 1: Remove multiple parameters
        #   Ensure order is maintained
        ['www.austintexas.gov?pone=first&ptwo=second&pone=third&pthree=fourth',[]],
        #   Ensure case is ignored
        ['www.austintexas.gov?a=1&A=1',[]],
        #   Ensure numbers don't cause issues
        ['www.austintexas.gov?1=1&2=123&7456=abc&1=1',[]],
        #REQ 2: Excluded parameters
        #   Simple use case
        ['www.austintexas.gov?a=1&b=2&a=1&b=2',['a']],
        #   Ensure case is ignored
        ['www.austintexas.gov?a=1&A=2&b=3',['A']],
        #   Ensure multiple params can be excluded
        ['www.austintexas.gov?a=1&b=2&c=3',['a','b']],
        #   Ensure all params can be excluded
        ['www.austintexas.gov?a=1&b=2&c=3',['a','b','c']],
        #   Ensure it's safe to exclude params that aren't included in the URL at all
        ['www.austintexas.gov?a=1&b=2',['extra']],
        ['www.austintexas.gov?a=1&b=2',['a','extra']],
        #   Ensure the same param can be excluded twice
        ['www.austintexas.gov?a=1&b=2',['a','a']],
        #REQ 3: set top-level domains to .gov
        #   Simple use case
        ['www.austintexas.net',[]],
        #   Test http://
        ['http://www.austintexas.net',[]],
        #   Test https://
        ['https://www.austintexas.ANARCHY',[]],
        #   Ensure non-top-level domains are maintained
        ['aus.tin.t.ex.as.com',[]],
        #   Test w/parameters
        ['www.austintexas.ANARCHY?a=1&b=2&c=3',[]],
        #   Test w/additional paths
        ['www.austintexas.a/b/c/file.type',[]],
        #   Test w/additional paths + parameters
        ['www.austintexas.a/b/c/file.type?one=first&two=2',[]]
    ]
)
def test_valid(url_before,excluded):
    url_after = validate_url(url_before,excluded)
    print()
    print("URL Before: "+str(url_before))
    print("URL After:  "+str(url_after))
    print("Excluded: "+str(excluded))
    params_before = get_params(url_before)
    params_after = get_params(url_after)

    #expected parameters
    params_expected = get_expected_params(params_before,excluded)
    assert (params_after == params_expected)

    #domains
    domains_before = get_domains(url_before)
    domains_after = get_domains(url_after)

    #ensure top-level domain is .gov
    assert(domains_after.group('top').lower() == '.gov')

    #ensure low-level domains have NOT been changed
    assert(domains_after.group('lower') == domains_before.group('lower'))


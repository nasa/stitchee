"""Initial configuration for tests."""
import pytest


def pytest_addoption(parser):
    """Sets up optional argument to keep temporary testing directory."""
    parser.addoption(
        '--keep-tmp',
        action='store_true',
        help='Keep temporary directory after testing. Useful for debugging.')


@pytest.fixture(scope='class')
def pass_options(request):
    """Adds optional argument to a test class."""
    request.cls.KEEP_TMP = request.config.getoption('--keep-tmp')

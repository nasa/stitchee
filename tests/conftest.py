import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--keep-tmp',
        action='store_true',
        help='Keep temporary directory after testing. Useful for debugging.')


@pytest.fixture(scope='class')
def pass_options(request):
    request.cls.KEEP_TMP = request.config.getoption('--keep-tmp')

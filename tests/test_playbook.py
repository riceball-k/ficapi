import pytest
from ficapi.playbook import InvalidMethod, Playbook, PlaybookParameter

PATH = '{url}/codes_of_conduct'
HEADER = {"Accept": "application/vnd.github.v3+json"}

repl = {
    'url': 'https://{fqdn}',
    'fqdn': 'api.github.com',
}


def test_exec_01():
    """exec 1: Success"""
    param = PlaybookParameter(path=PATH, header=HEADER, method='get')
    r = Playbook(param).exec(repl)
    assert r.status_code == 200


def test_exec_02():
    """exec 2: KeyError"""
    param = PlaybookParameter(path=PATH, header=HEADER, method='get')
    with pytest.raises(KeyError):
        Playbook(param).exec({})


def test_replace_01():
    """replace 1: Success"""
    param = PlaybookParameter(path=PATH, header=HEADER, method='get')
    Playbook(param).replace(repl)


def test_replace_02():
    """replace 2: KeyError"""
    param = PlaybookParameter(path=PATH, header=HEADER, method='get')
    with pytest.raises(KeyError):
        Playbook(param).replace({})


def test_method_01():
    """method 1: get and post"""
    PlaybookParameter(path=PATH, header=HEADER, method='get')
    PlaybookParameter(path=PATH, header=HEADER, method='post')


def test_method_02():
    """method 2: put"""
    with pytest.raises(InvalidMethod):
        PlaybookParameter(path=PATH, header=HEADER, method='put')


def test_method_03():
    """method 3: patch"""
    with pytest.raises(InvalidMethod):
        PlaybookParameter(path=PATH, header=HEADER, method='patch')


def test_method_04():
    """method 4: hoge"""
    with pytest.raises(InvalidMethod):
        PlaybookParameter(path=PATH, header=HEADER, method='hoge')

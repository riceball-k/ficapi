from pathlib import Path

import pytest
from ficapi.fictoken import FicToken
from ficapi.mycipher import DecryptionError, PasswordNotSet

PASSWORD = 'test'
INVALID_PASSWORD = 'hoge'
TOKEN_ID = 'abcdefghijklmn'

path = Path('tests/token')


def test_read_01():
    """read valid token"""
    token = FicToken(path / 'token_valid.json', password=PASSWORD)
    assert token.is_valid is True


def test_read_02():
    """read expired token"""
    token = FicToken(path / 'token_expired.json', password=PASSWORD)
    assert token.is_valid is False


def test_read_03():
    """password error"""
    with pytest.raises(DecryptionError):
        FicToken(path / 'token_valid.json', password=INVALID_PASSWORD)


def test_read_04():
    """password not set"""
    with pytest.raises(PasswordNotSet):
        FicToken(path / 'token_valid.json', password=None)


def test_read_05():
    """required attribute not found"""
    with pytest.raises(KeyError):
        FicToken({}, password=PASSWORD)


def test_write_01():
    """write"""
    token = FicToken(path / 'token_valid.json', password=PASSWORD)
    token.write(path / 'hoge.json')
    token2 = FicToken(path / 'hoge.json', password=PASSWORD)
    assert token.id == token2.id
    # 削除しとく
    (path / 'hoge.json').unlink()

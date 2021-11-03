# Copyright 2021 riceball-k
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Encryption Module for FicAPI

Encryption of character strings and decryption of cipher strings
using hash values generated from password strings.
"""
from __future__ import annotations

import binascii
import getpass
import hashlib
from typing import Any

from Crypto.Cipher import AES


class DecryptionError(Exception):
    """復号化エラー"""


class PasswordNotSet(Exception):
    """パスワード未設定エラー"""


def input_password() -> str | None:
    """パスワードをコンソールから入力する
    成功の場合、パスワード文字列からハッシュ値を計算し保持する

    Returns:
        str: パスワード
        None: パスワード入力失敗
    """
    p1 = getpass.getpass('\ninput password: ')
    p2 = getpass.getpass('       confirm: ')
    if p1 == p2:
        return p1
    else:
        return None


class MyCipher:
    """暗号化クラス"""
    def __init__(self, password: str | None = None):
        """暗号化クラスの初期化
        パスワードからハッシュ値を計算し保持する
        パスワードがNoneの場合にはハッシュ値もNoneとなるが、
        Noneのままで暗号化・復号化を実施すると例外が発生する

        Args:
            password (str | None): パスワード

        Raises:
            TypeError: 引数の型が不正
        """
        self.secret: bytes | None
        if password is None:
            self.secret = None
        elif isinstance(password, str):
            self.setsecret(password)
        else:
            raise TypeError(f'invalid arg type {type(password)}, '
                            f'must be {str}.')

    def setsecret(self, password: str) -> None:
        """パスワード文字列からハッシュ値を計算し保持する

        Args:
            password (str): パスワード文字列

        Raises:
            TypeError: 引数の型が不正
        """
        if not isinstance(password, str):
            raise TypeError(f'invalid arg type {type(password)}, '
                            f'must be {str}.')

        self.secret = self.sha256(password)

    @property
    def _cipher(self) -> Any:
        """暗号化オブジェクト（cipher）を返す

        Raises:
            PasswordNotSet: self.secretがNone

        Returns:
            Any: AES.new()によりEaxMODEが返される
        """
        if self.secret is None:
            raise PasswordNotSet('password is not set.')

        return AES.new(self.sha256(self.secret),
                       AES.MODE_EAX,
                       self.md5(self.secret))

    def sha256(self, text: str | bytes) -> bytes:
        """文字列のハッシュ値を返す（sha256）

        Args:
            text (str | bytes): 文字列

        Returns:
            bytes: ハッシュ値（sha256）

        Raises:
            TypeError: 引数の型が不正
        """
        if isinstance(text, str):
            return hashlib.sha256(text.encode('utf-8')).digest()
        elif isinstance(text, bytes):
            return hashlib.sha256(text).digest()
        else:
            raise TypeError(f'invalid arg type {type(text)}, '
                            f'must be {str} or {bytes}.')

    def md5(self, text: str | bytes) -> bytes:
        """文字列のハッシュ値を返す（md5）

        Args:
            text (str | bytes): 文字列

        Returns:
            bytes: ハッシュ値（md5）

        Raises:
            TypeError: textの型が不正
        """
        if isinstance(text, str):
            return hashlib.md5(text.encode('utf-8')).digest()
        elif isinstance(text, bytes):
            return hashlib.md5(text).digest()
        else:
            raise TypeError(f'invalid arg type {type(text)}, '
                            f'must be {str} or {bytes}.')

    def encrypt(self, text: str) -> str:
        """文字列を暗号化する

        Args:
            text (str): 文字列（平文）

        Returns:
            str: 暗号化した文字列

        Raises:
            TypeError: textの型が不正
        """
        if not isinstance(text, str):
            raise TypeError(f'invalid arg type {type(text)}, '
                            f'must be {str}.')

        return self._cipher.encrypt(text.encode('utf-8')).hex()

    def decrypt(self, text: str) -> str:
        """暗号文字列を復号化する

        Args:
            text (str): 文字列（暗号）

        Returns:
            str: 復号化した文字列

        Raises:
            TypeError: textの型が不正
            DecryptionError: 復号化失敗
        """
        if not isinstance(text, str):
            raise TypeError(f'invalid arg type {type(text)}, '
                            f'must be {str}.')

        try:
            return self._cipher.decrypt(binascii.a2b_hex(text)).decode('utf-8')
        except PasswordNotSet as e:
            raise PasswordNotSet(e)
        except UnicodeDecodeError:
            raise DecryptionError("Don't decrypt the text")

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

"""Token Management Module for FicAPI

Manage authentication tokens for the FIC API access.

The authentication token can be read from the token file or
retrieved from the Response object after accessing keystone.
"""
from __future__ import annotations

import json
from copy import copy, deepcopy
from datetime import datetime
from os import PathLike
from pathlib import Path

import requests

from . import mycipher

TOKENID = 'X-Subject-Token'
EXPIRES = 'expires_at'


class FicToken:
    """Tokenを保持するクラス"""
    def __init__(self,
                 token: PathLike | str | dict | None = None,
                 *,
                 password: str | None = None
                 ):
        """トークンの作成

        Args:
            token (PathLike | str | dict | None):
                - PathLike | str: ファイル名
                - dict: トークンデータ
            password (str | None): パスワード

        Raises:
            TypeError: 引数の型が不正
        """
        if not isinstance(password, (str, type(None))):
            raise TypeError(f'invalid arg type {type(password)}, '
                            f'must be {str} or None.')
        self._cipher = mycipher.MyCipher(password)

        self._token = {
            TOKENID: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            EXPIRES: '2001-01-01T00:00:00.000000Z'
        }
        if token is None:
            pass
        elif isinstance(token, (PathLike, str)):
            self.read(token)
        elif isinstance(token, dict):
            self._token = copy(token)
        else:
            raise TypeError(f'invalid arg type {type(token)}, '
                            f'must be {PathLike}, {str} or {dict}.')

        self._check_token()

    def __str__(self) -> str:
        """トークンIDを返す"""
        return self.id

    def __repr__(self) -> str:
        """トークンIDを返す（token_id=xxxxx）"""
        return repr(f'token_id={self.id}')

    def __bool__(self) -> bool:
        """トークンの有効期限判定

        Returns:
            bool: 有効期限内ならTrue、有効期限切れならFalse
        """
        return self.is_valid

    def _check_token(self) -> None:
        """トークンに必須要素（'X-Subject-Token'と'expires_at'）
        があるかチェックする

        Raises:
            KeyError: 必須要素がない
        """
        if not {TOKENID, EXPIRES} <= set(self._token):
            raise KeyError(f'"{TOKENID}" or "{EXPIRES}" is not found in token')

    @property
    def id(self) -> str:
        """トークンIDを返す

        Returns:
            str: トークンID
        """
        return self._token[TOKENID]

    @property
    def expire_time(self) -> datetime:
        """トークンの有効期限を返す

        Returns:
            datetime: 有効期限（タイムゾーン有り）
        """
        return datetime.fromisoformat(
            self._token[EXPIRES].replace('Z', '+00:00')
        )

    @property
    def is_valid(self) -> bool:
        """トークンの有効期限判定

        Returns:
            bool: 有効期限内ならTrue、有効期限切れならFalse
        """
        return self.expire_time > datetime.now().astimezone()

    def read(self, file: PathLike | str, password: str | None = None) -> None:
        """ファイル（JSON形式）からトークンを読み込む
        トークンIDは復号化する

        Args:
            file (PathLike | str): ファイル名
            password (str | None): パスワード

        Raises:
            TypeError: 引数の型が不正
            KeyError: 必須要素がない
        """
        if not isinstance(file, (PathLike, str)):
            raise TypeError(f'invalid arg type {type(file)}, '
                            f'must be {PathLike} or {str}.')
        if isinstance(password, str):
            cipher = mycipher.MyCipher(password)
        elif password is None:
            cipher = self._cipher
        else:
            raise TypeError(f'password must be {str}.')

        self._token = json.loads(Path(file).read_text(encoding='utf-8'))
        self._check_token()
        self._token[TOKENID] = cipher.decrypt(self._token[TOKENID])
        self._cipher = cipher

    def write(self, file: PathLike | str, password: str | None = None) -> None:
        """ファイルへトークンを書き込む（JSON形式）
        トークンIDは暗号化する

        Args:
            file (PathLike | str): ファイル名
            password (str | None): パスワード

        Raises:
            TypeError: 引数の型が不正
        """
        if not isinstance(file, (PathLike, str)):
            raise TypeError(f'invalid arg type {type(file)}, '
                            f'must be {PathLike} or {str}.')
        if isinstance(password, str):
            cipher = mycipher.MyCipher(password)
        elif password is None:
            cipher = self._cipher
        else:
            raise TypeError(f'password must be {str}.')

        token = deepcopy(self._token)
        token[TOKENID] = cipher.encrypt(token[TOKENID])
        Path(file).write_text(json.dumps(token, indent=4), encoding='utf-8')
        self._cipher = cipher

    def update(self, response: requests.Response) -> None:
        """レスポンスオブジェクトからトークンを読み込む
        以下の必須情報がない場合には例外が発生する
        - headerには 'X-Subject-Token' があること
        - bodyには 'expires_at' があること

        Args:
            response (requests.Response): レスポンスオブジェクト

        Raises:
            TypeError: 引数の型が不正
            ValueError: レスポンスオブジェクトに必須情報がない
        """
        if not isinstance(response, requests.Response):
            raise TypeError(f'invalid arg type {type(response)}, '
                            f'must be {requests.Response}.')

        body = response.json()
        if TOKENID not in response.headers:
            raise ValueError(f'"{TOKENID}" is not found in response header.')
        if EXPIRES not in body['token']:
            raise ValueError(f'"{EXPIRES}" is not found in response body.')

        # トークンの置き換え
        self._token = dict(response.headers)
        self._token[EXPIRES] = body['token'][EXPIRES]

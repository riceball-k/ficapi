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

"""Flexible InterConnect API Access Module

This module is a Python library that provides API access functions
for Flexible InterConnect, a network service of NTT Communications.

It has functions to automatically acquire a authentication token
(reuse it within the expiration date, and reacquire when expire),
API access with parameters from JSON files or DICT,
and the ability to specify resource IDs by resource name.
"""
from __future__ import annotations

import configparser
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from os import PathLike
from pathlib import Path

from requests import Response

if __name__ == '__main__':
    from fictoken import FicToken
    from mycipher import MyCipher, PasswordNotSet
    from playbook import Playbook, PlaybookParameter
else:
    from .fictoken import FicToken
    from .mycipher import MyCipher, PasswordNotSet, input_password
    from .playbook import Playbook, PlaybookParameter


class FicAPI:
    def __init__(self,
                 file: PathLike | str = './ficapi.ini',
                 password: str | None = None
                 ):
        """オブジェクトの初期化
            コンフィグファイル（.iniファイル）を読み込む
            トークンファイルがあれば読み込む

        Args:
            file (PathLike | str): .iniファイル名
            password (str | None): パスワード
        """
        if not isinstance(file, (PathLike, str)):
            raise TypeError(f'invalid arg type {type(file)}, '
                            f'must be {PathLike} or {str}.')
        if not isinstance(password, (str, type(None))):
            raise TypeError(f'password must be {str} or None.')

        if password is None:
            password = input_password()
            if password is None:
                raise PasswordNotSet('password unmatched.')
        self._cipher = MyCipher(password)
        self._token = FicToken(password=password)

        # コンフィグファイル読込
        self.config = configparser.ConfigParser()
        with Path(file).open(encoding='utf-8') as f:
            self.config.read_file(f)
        for section, option in (('auth', 'api_endpoint'),
                                ('auth', 'api_key'),
                                ('auth', 'api_secret'),
                                ('tenant', 'tenant_id')):
            if not self.config.has_option(section, option):
                raise ValueError(
                    f'required option "{option}" not found in .ini')
        self.tenant = self.config['tenant']
        self.tenant['token_id'] = self._token.id
        self.token_file = Path(f'./.{self.tenant["tenant_id"]}.token')

    def get_token(self) -> None:
        """トークンを取得する
        取得済みトークンの有効期限が切れている場合は再取得する
        """
        if not self._token and self.token_file.is_file():
            self._token.read(self.token_file)
        if not self._token:
            # プレイブックを実行してトークンを取得する
            playbook = PlaybookParameter(
                method="post",
                path="{api_endpoint}/keystone/v3/auth/tokens",
                header={
                    "Content-Type": "application/json"
                },
                body={
                    "auth": {
                        "identity": {
                            "methods": [
                                "password"
                            ],
                            "password": {
                                "user": {
                                    "domain": {
                                        "id": "default"
                                    },
                                    "name": self._cipher.decrypt(
                                        self.config.get('auth', 'api_key')
                                    ),
                                    "password": self._cipher.decrypt(
                                        self.config.get('auth', 'api_secret')
                                    ),
                                }
                            }
                        },
                        "scope": {
                            "project": {
                                "id": "<tenant_id>"
                            }
                        }
                    }
                }
            )
            response = Playbook(playbook).exec(self.tenant)
            response.raise_for_status()
            self._token.update(response)
        self.tenant['token_id'] = self._token.id
        # トークンをファイルに出力する
        self._token.write(self.token_file)

    def get_resources(self):
        """resouceNameをキー、resourceIdを値とするオプションをself.tenantに追加する
        """
        @dataclass
        class Resource:
            type: str
            name: str
            id: str
            id2: str = ''

        # プレイブック実行
        self.request(
            {
                'name': 'Show Tenants',
                'method': 'get',
                'path': '{api_endpoint}/fic-monitoring/v1/'
                        'flexible-ic/tenants/{tenantId}',
                'header': {
                    'X-Auth-Token': '<token_id>',
                    'Content-Type': 'application/json'
                },
            }
        )
        response_body = self.r.json()

        # self.tenantにテナント名を追加
        self.tenant['tenantName'] = response_body['tenantName']

        # self.tenantにリソース名とリソースIDの情報を追加
        resources: tuple[Resource, ...] = (
            Resource('ports', 'name', 'portId', ""),
            Resource('connections', 'name', 'connectionId', ""),
            Resource('routers', 'name', 'routerId', ""),
        )
        for res in resources:
            for resource in response_body[res.type]:
                res_name = resource[res.name]
                res_id = resource[res.id]
                self.tenant[res_name] = res_id
                self.tenant[res_id] = res_name

        # self.tenantにfwIdとnatIdの情報を追加
        resources = (
            Resource('routers', 'name', 'fwId', 'natId'),
        )
        for res in resources:
            for resource in response_body[res.type]:
                res_name = resource[res.name]
                res_fwid = resource[res.id]
                res_natid = resource[res.id2]
                if res_fwid:
                    self.tenant[f'{res_name}_{res.id}'] = res_fwid
                    self.tenant[res_fwid] = f'{res_name}_{res.id}'
                if res_natid:
                    self.tenant[f'{res_name}_{res.id2}'] = res_natid
                    self.tenant[res_natid] = f'{res_name}_{res.id2}'

    def request(
        self,
        playbook: dict | PathLike | str | Playbook | PlaybookParameter
    ) -> Response:
        """プレイブックの実行

        Args:
            playbook (dict | PathLike | str | Playbook | PlaybookParameter):
                - dict: パラメータ辞書
                - PathLike | str: ファイル名
                - Playbook: プレイブック
                - PlaybookParameter: パラメータオブジェクト
        """
        self.get_token()

        # self.tenantの"from", "to"を時刻に書き換える
        tenant = deepcopy(self.tenant)
        _from: str = tenant.get('from', '-7days').strip()
        _to: str = tenant.get('to', 'now').strip()
        if _to == 'now':
            tenant['to'] = str(datetime.now().astimezone())
        if _from.endswith('days'):
            dt = timedelta(days=int(_from[:-4]))
            tenant['from'] = str(datetime.fromisoformat(tenant['to']) + dt)

        # 実行
        if isinstance(playbook, Playbook):
            self.r = playbook.exec(tenant)
        else:
            self.r = Playbook(playbook).exec(tenant)
        return self.r

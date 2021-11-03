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

"""Playbook Module for FicAPI

This module executes API access based on API access parameters in
JSON file or dict data format.
In this module, the parameter object is named "Playbook".
"""
from __future__ import annotations

import dataclasses
import json
import re
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any, Mapping

import requests


class InvalidMethod(Exception):
    """Invalid Method"""


@dataclass(frozen=True)
class PlaybookParameter:
    """Playbookのパラメータ保持用データクラス
    """
    method: str
    path: str
    name: str = ""
    overview: str = ""
    header: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    parameter: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """アトリビュートの型チェックとmethodの値チェック

        Raises:
            TypeError: アトリビュートの型が不正
            InvalidMethod: 無効なmethod
        """
        if not all((isinstance(self.method, str),
                    isinstance(self.path, str),
                    isinstance(self.name, str),
                    isinstance(self.overview, str),
                    isinstance(self.header, dict),
                    isinstance(self.body, dict),
                    isinstance(self.parameter, dict),
                    )):
            raise TypeError(f'{type(self).__name__}: '
                            f'attribute type is invalid.')

        if self.method not in ('get', 'post'):
            raise InvalidMethod(
                f'{type(self).__name__}: "{self.method}" method is not '
                f'implemented, only "get" and "post".'
            )

    def replace(self, repl_table: Mapping[str, str]) -> PlaybookParameter:
        """各パラメータの変数部分を置換し新しいPlaybookParameterを返す
        置換対象は以下の通り
        - pathの '{...}'
        - header, body, parameterの '<...>'
        '...' をキーとして、repl_table['...'] に置換する

        再帰的に置換するので、
            repl_table = {
                'hoge': '{fuga}',
                'fuga': 'abcdefg'
            }
        の場合、
            'path': '{hoge}'
        は
            'path': 'abcdefg'
        に置換される

        Args:
            repl_table (Mapping[str, str]):
                置換前文字列をキー、置換後文字列を値とする辞書

        Returns:
            PlaybookParameter: 置換後のオブジェクト

        Raised:
            KeyError: repl_tableの置換前文字列をキーとす要素がない
        """
        def _replace(m: re.Match) -> str:
            return repl_table[m.group(1)]

        if not isinstance(repl_table, Mapping):
            raise TypeError(f'invalid arg type {type(repl_table)}, '
                            f'must be {Mapping}.')

        try:
            path = self.path
            while '{' in path:
                path = re.sub(r'{([^{}]+?)}', _replace, path)

            header = json.dumps(self.header)
            while '<' in header:
                header = re.sub(r'<([^<>]+?)>', _replace, header)

            body = json.dumps(self.body)
            while '<' in body:
                body = re.sub(r'<([^<>]+?)>', _replace, body)

            parameter = json.dumps(self.parameter)
            while '<' in parameter:
                parameter = re.sub(r'<([^<>]+?)>', _replace, parameter)

        except KeyError as e:
            raise KeyError(f'repl_table does not have "{str(e)}".')

        return dataclasses.replace(self,
                                   path=path,
                                   header=json.loads(header),
                                   body=json.loads(body),
                                   parameter=json.loads(parameter),
                                   )


class Playbook:
    def __init__(self, playbook: PlaybookParameter | dict | PathLike | str):
        """Playbookを読み込む

        Args:
            playbook (dict | PathLike | str | PlaybookParameter): Playbook情報
                - PlaybookParameter: PlaybookParameterオブジェクト
                - dict: PlaybookParameter形式の辞書
                - PathLike | str: JSONファイル名

        Raises:
            TypeError: 引数の型が不正
            ValueError: method が "get" または "post" ではない
            その他: 実行した関数・メソッドで発生する例外
        """
        self.playbook: PlaybookParameter
        self.new_playbook: PlaybookParameter | None = None

        if isinstance(playbook, PlaybookParameter):
            self.playbook = playbook
        elif isinstance(playbook, dict):
            self.playbook = PlaybookParameter(**playbook)
        elif isinstance(playbook, (PathLike, str)):
            self.playbook = PlaybookParameter(
                **json.loads(Path(playbook).read_text(encoding='utf-8'))
            )
        else:
            raise TypeError(f'invalid arg type {type(playbook)}.')

    def replace(self, repl_table: Mapping[str, str]) -> None:
        """PlaybookParameterの置換
        インプレイスで置換する

        Args:
            repl_table (Mapping[str, str]): 置換前文字列をキー、置換後文字列を値とする辞書

        Raises:
            TypeError: 引数の型が不正
        """
        if not isinstance(repl_table, Mapping):
            raise TypeError(f'invalid arg type {type(repl_table)}, '
                            f'must be {Mapping}.')
        self.playbook = self.playbook.replace(repl_table)

    def exec(self, repl_table: Mapping[str, str] | None = None
             ) -> requests.Response:
        """Playbookを実効する

        Args:
            repl_table (Mapping[str, str] | None): 文字列置換テーブル

        Raises:
            TypeError: repl_tableの型が不正
            ValueError: method が "get" または "post" ではない

        Returns:
            requests.Response: レスポンスオブジェクト
        """
        if isinstance(repl_table, Mapping):
            self.new_playbook = self.playbook.replace(repl_table)
        elif repl_table is None:
            self.new_playbook = self.playbook.replace({})
        else:
            raise TypeError(f'invalid arg type {type(repl_table)}, '
                            f'must be {Mapping}.')

        if self.new_playbook.method == 'get':
            return requests.get(self.new_playbook.path,
                                headers=self.new_playbook.header,
                                params=self.new_playbook.parameter)
        elif self.new_playbook.method == 'post':
            return requests.post(self.new_playbook.path,
                                 headers=self.new_playbook.header,
                                 json=self.new_playbook.body)
        else:
            raise ValueError(f'invalid method "{self.new_playbook.method}", '
                             f'must be "get" or "post".')

<!-- omit in toc -->
# Flexible InterConnect API Access Module

## 1. 概要

NTTコミュニケーションズのネットワークサービス「Flexible InterConnect」のAPI利用を簡略化するPythonのライブラリです。

- 認証トークンの取得・有効期限管理の自動化
  - 取得した認証トークンはファイル保存される
- 認証トークン取得に必要となるAPI鍵・API秘密鍵・テナントIDを設定ファイルから読み込み
- 秘匿性の高い情報の暗号化
  - 設定ファイル内のAPI鍵・API秘密鍵
  - トークンファイル内の認証トークン
- API要求のパラメータをJSONファイル化した「Playbook」によるアクセス
  - dict型データとしても指定可能
- パラメータでリソース指定する際に、リソースID（portID、connectionId、routerId等）ではなくリソース名で指定可能
  - リソース情報（リソース名・リソースID）はAPIで取得するため設定ファイルに記述不要

## 2. 必須ライブラリ

- pycryptodome
- requests

## 3. インストール方法

このパッケージはPyPIに登録していないので、GitHubからクローンしてからパッケージを作成しインストールしてください。

```powershell
> git clone https://github.com/riceball-k/ficapi
> cd ficapi
> py setup.py sdist
> py -m pip install dist\ficapi-x.x.x.tar.gz
```

## 4. 使い方

### 4.1. 設定ファイルを作成する

FicAPIクラスのインスタンスを作成しAPIアクセスしますが、設定ファイルからAPI鍵などを読み込むので、まずは設定ファイルを作成します。
デフォルトの設定ファイル名は `./ficapi.ini` です。

#### 4.1.1. FICポータルで必要情報を確認する

FICポータルにログインし以下の情報をメモします。情報漏洩すると面倒なので慎重に取り扱ってください。（なおAPI秘密鍵だけはFICポータル上で再発行できます。再発行すると古いものは無効化されます。）

- API鍵
- API秘密鍵
- テナントID

#### 4.1.2. 設定ファイルを作成する

`create_ficapi_ini.exe`を実行し、カレントディレクトリに`ficapi.ini`を作成します。
（`create_ficapi_ini.exe`はPythonのインストールディレクトリの`Scripts`ディレクトリにインストールされます。）

作成時にパスワードを聞かれるので入力してください。**このパスワードはFICポータルのログインパスワードとは無関係**なので好きな文字列を入力してください。（文字種・文字数の指定や制限なし）

パスワードはAPI鍵・API秘密鍵などの暗号化および復号化で使用します。FicAPIクラスのインスタンス作成時にパスワードが必要となりますので忘れないでください。忘れた場合は設定ファイルを再作成してください。

`create_ficapi_ini.exe`では、`ficapi.ini`に以下の情報を保存します。

- api_endpoint
- api_key
- api_secret
- tenant_id （およびtenantId）

**設定ファイルサンプル**:

設定ファイルのサンプルです。

```ini
[DEFAULT]
; FIC APIエンドポイント
api_endpoint = https://api.ntt.com

[auth]
; API鍵（暗号化した文字列）
api_key = xxxxxxxxxxxxxxxxxxx
; API秘密鍵（暗号化した文字列）
api_secret = xxxxxxxxxxxxxxxxxxx

[tenant]
; テナント
tenant_id = xxxxxxxxxxxxxxxxxxx
router     = ルータ名
port       = ポート名
connection = コネクション名

; xxxxx_idの定義
router_id     = {{router}}
port_id       = {{port}}
connection_id = {{connection}}
firewall_id   = {{router}_fwid}
nat_id        = {{router}_natid}

; xxxxx_idの別名定義（xxxxxId）
tenantId     = {tenant_id}
routerId     = {router_id}
portId       = {port_id}
connectionId = {connection_id}
firewallId   = {firewall_id}
natId        = {nat_id}

; 取得期間の開始日時（-nndaysならtoのnn日前）
; ex:2019-04-02T13:08:43+09:00
; ex:-30days
from = -90days

; 取得期間の終了日時（nowなら現在日時）
; ex:2019-04-02T13:08:43+09:00
to = now
```

**必須パラメータ**:

- DEFAULT.api_endpoint
  - FIC APIのエンドポイントURL（文字列）

- auth.api_key
  - FICポータルのログインユーザ毎に設定されているAPI鍵（文字列）を暗号化した文字列

- auth.api_secret
  - FICポータルのログインユーザ毎に設定されているAPI秘密鍵（文字列）を暗号化した文字列

- tenant.tenant_id
  - FICポータルから取得した、テナントID（文字列）

**任意パラメータ**:

- tenant.xxxx
  - Playbookで指定している `{xxxx}` の置換文字列を設定する
  - 再帰的に置換される（内側の`{}`から順番に置換する）

### 4.2. サンプルプログラム

#### 4.2.1. Pythonスクリプト

```python
import ficapi
import json

fic = ficapi.FicAPI('./ficapi.ini')
fic.get_resources()
r = fic.request('playbook/FIC_Show_Tenants.json')
print(r.headers)
print(json.dumps(r.json(), indent=4))
```

#### 4.2.2. Playbook

```json
{
    "name": "Show Tenants",
    "overview": "指定したテナント情報を取得します。",
    "method": "get",
    "path": "{api_endpoint}/fic-monitoring/v1/flexible-ic/tenants/{tenantId}",
    "header": {
        "X-Auth-Token": "<token_id>",
        "Content-Type": "application/json"
    },
    "body": {},
    "parameter": {}
}
```

## 5. Playbookの作り方

[SDPFのページ](https://sdpf.ntt.com/services/fic/api-references/)から「サービス別のAPI一覧」にアクセスし、コピペでJSONファイルを作成する。

### 5.1. 書式

- JSONの書式に完全準拠していること
- ファイル名は任意でよい

以下の様な記述になります。

```json
{
  "name": "API Name",
  "overview": "説明文",
  "method": "get",
  "path": "{api_endpoint}/aaa/bbb/ccc",
  "header": {
      "X-Auth-Token": "<token_id>",
      "Content-Type": "application/json"
  },
  "body": {},
  "parameter": {}
}
```

### 5.2. パラメータ説明

#### 5.2.1. 必須パラメータ

- `method`
  - httpのメソッド（文字列型）
  - `get`, `post` のみ指定可能
    - 他のmethodにも対応することは容易にできるが、破壊的な変更も実施できてしまうため、安全を優先して利用可能methodを制限している。
- `path`
  - アクセス先URL（文字列型）
- `header`
  - httpヘッダ（辞書型）

#### 5.2.2. 省略可能パラメータ

- `name`
  - APIの名前（文字列型）
- `overview`
  - APIの機能概要（文字列型）
- `body`
  - request body（辞書型）
  - 主にpost methodで使用
- `parameter`
  - request parameter（辞書型）
  - 主にget methodで使用

### 5.3. 文字列置換について

- パラメータ文字列内の`{}`や`<>`で囲った部分は文字列置換されます。
- 対象となるのは`path`、`header`、`body`、`parameter`だけです。
- 置換した文字列にさらに置換できる部分がある場合、繰り返し実施されます。（循環置換しないように注意）

  | パラメータ  | 置換文字列       |
  | ----------- | ---------------- |
  | `path`      | `{xxxx}` の xxxx |
  | `header`    | `<xxxx>` の xxxx |
  | `body`      | `<xxxx>` の xxxx |
  | `parameter` | `<xxxx>` の xxxx |

#### 5.3.1. 置換テーブル

置換テーブルは以下の値を参照します。

- 設定ファイルのtenantセクション
  - オプション名から値への置換
- FicAPI.get_resource()で取得したリソース情報
  - リソース名からリソースIDへの置換
  - リソースIDからリソース名への置換

### 5.4. 作成例

#### 5.4.1. 例：`List Areas`の場合

1. [APIリファレンス](https://sdpf.ntt.com/services/docs/fic/api-references/area/rsts/Area.html)にアクセスし以下の情報をコピペする。

   - API名

    ```text
    List Areas
    ```

   - Overview

    ```text
    エリア情報の一覧を取得します。
    ```

   - HTTP Request Method

    ```text
    GET
    ```

   - HTTP Request Path

    ```text
    {api_endpoint}/fic-eri/v1/areas
    ```

   - HTTP Request Header

    ```text
    X-Auth-Token: <token_id>
    Content-Type: application/json
    ```

   - HTTP Request Body

    ```text
    none
    ```

   - Request Parameter

    ```text
    none
    ```

2. Playbook（JSONファイル）を作成する

   ```json
   {
     "name": "List Areas",
     "overview": "エリア情報の一覧を取得します。",
     "method": "get",
     "path": "{api_endpoint}/fic-eri/v1/areas",
     "header": {
         "X-Auth-Token": "<token_id>",
         "Content-Type": "application/json"
     }
   }
   ```

#### 5.4.2. 例：`List NatCounts`の場合

＜ポイント＞

`HTTP Request Path` に `{routerId}` があるので、設定ファイルに`routerID = xxx`を設定しておく必要がある。

1. [APIリファレンス](https://sdpf.ntt.com/services/docs/fic/api-references/support-monitoring/rsts/Monitoring.html#list-natcounts)にアクセスし以下の情報をコピペする。

   - API名

    ```text
    List NatCounts
    ```

   - Overview

    ```text
    指定したルーターに紐づくナットのセッション数情報の一覧を取得します。
    ```

   - HTTP Request Method

    ```text
    GET
    ```

   - HTTP Request Path

    ```text
    {api_endpoint}/fic-monitoring/v1/flexible-ic/tenants/{tenantId}/routers/{routerId}/natCounts
    ```

   - HTTP Request Header

    ```text
    X-Auth-Token: <token_id>
    Content-Type: application/json
    ```

   - HTTP Request Body

    ```text
    none
    ```

   - Request Parameter

    | item     | mandatory | format | enum | description    |
    | -------- | --------- | ------ | ---- | -------------- |
    | tenantId | ○         | string | -    | 対象テナントID |
    | routerId | ○         | string | -    | 対象ルーターID |

2. Playbook（JSONファイル）を作成する

   ```json
   {
      "name": "List NatCounts",
      "overview": "指定したルーターに紐づくナットのセッション数情報の一覧を取得します。",
      "method": "get",
      "path": "{api_endpoint}/fic-monitoring/v1/flexible-ic/tenants/{tenantId}/routers/{routerId}/natCounts",
      "header": {
          "X-Auth-Token": "<token_id>",
          "Content-Type": "application/json"
      }
   }
   ```

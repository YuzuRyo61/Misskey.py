# Misskey.py
Misskeyインスタンス用のPythonライブラリです。

[Misskey](https://github.com/syuilo/misskey)は[syuilo](https://github.com/syuilo)氏が作成した分散型SNSソフトウェアです。

---

## 使い方

### ライブラリのインポートと初期化
```python
from Misskey import Misskey

misskey = Misskey("misskey.xyz") # インスタンスアドレスを入力、未入力の場合は"misskey.xyz"を指定します。
```

#### use session key
```python
from Misskey import Misskey

# appSecretとaccessTokenを指定する場合
misskey = Misskey("misskey.xyz", appSecret="abcdef123...", accessToken="abcdef123...")
```

**or**

```python
from Misskey import Misskey

# apiTokenを指定する場合(apiTokenはappSecretとaccessTokenをsha256ハッシュ化したもの)
misskey = Misskey("misskey.xyz", apiToken="abcdef123...")
```
# Misskey.py

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Python test](https://github.com/YuzuRyo61/Misskey.py/actions/workflows/test.yml/badge.svg?branch=v4)](https://github.com/YuzuRyo61/Misskey.py/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/YuzuRyo61/Misskey.py/branch/v4/graph/badge.svg?token=97A1HJHUMW)](https://codecov.io/gh/YuzuRyo61/Misskey.py)

> Japanese version available. [Click Here](https://github.com/YuzuRyo61/Misskey.py/blob/v2/README-JP.md).

This script is Python library for Misskey Instance.

This library is only available in Python3.

[Misskey](https://github.com/misskey-dev/misskey) is made by [syuilo](https://github.com/syuilo).

---

## How to install

### Use pip (Recommend)

```bash
pip install Misskey.py
# or
pip3 install Misskey.py
```

## usage

### import library (init)

```python
from misskey import Misskey

misskey = Misskey("misskey.io")  # Input instance address (If leaved no attribute, it sets "misskey.io")
```

#### Use token key

```python
from misskey import Misskey

# If use the token
misskey = Misskey("misskey.io", i="abcdef123...")
```

### Create token

```python
from misskey import Misskey
from misskey.legacy.Util import MiAuth

auth = MiAuth("misskey.io", name="misskey.py")
# Get Authentication URL, then send to client browser
url = auth.getUrl()
# After permission granted, run this function
token = auth.check()
# To use misskey.py with created token, please below
misskey = Misskey("misskey.io", i=token["token"])  # or: misskey = misskey("misskey.io", i=auth.token)
```

## Other

**Pull requests are HUGE WELCOME!**

We hope you will contribute to the completion of the library by all means.

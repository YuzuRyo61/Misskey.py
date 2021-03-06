# Misskey.py

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Build Status](https://travis-ci.org/YuzuRyo61/Misskey.py.svg?branch=v1)](https://travis-ci.org/YuzuRyo61/Misskey.py)
[![Coverage Status](https://coveralls.io/repos/github/YuzuRyo61/Misskey.py/badge.svg?branch=v1)](https://coveralls.io/github/YuzuRyo61/Misskey.py?branch=v1)
[![Documentation Status](https://readthedocs.org/projects/misskeypy/badge/?version=latest)](https://misskeypy.readthedocs.io/en/latest/?badge=latest)

> Japanese version available. [Click Here](https://github.com/YuzuRyo61/Misskey.py/blob/v2/README-JP.md).

This script is Python library for Misskey Instance.

This library is only available in Python3.

[Misskey](https://github.com/syuilo/misskey) is made by [syuilo](https://github.com/syuilo).

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
from Misskey import Misskey

misskey = Misskey("misskey.io") # Input instance address (If leaved no attribute, it sets "misskey.io")
```

#### Use token key

```python
from Misskey import Misskey

# If use the token
misskey = Misskey("misskey.io", i="abcdef123...")
```

### Create token

```python
from Misskey import Misskey
from Misskey.Util import MiAuth

auth = MiAuth("misskey.io", name="Misskey.py")
# Get Authentication URL, then send to client browser
url = auth.getUrl()
# After permission granted, run this function
token = auth.check()
# To use Misskey.py with created token, please below
misskey = Misskey("misskey.io", i=token["token"]) # or: misskey = Misskey("misskey.io", i=auth.token)
```

## Other

**Pull requests are HUGE WELCOME!**

We hope you will contribute to the completion of the library by all means.

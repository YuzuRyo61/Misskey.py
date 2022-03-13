# Misskey.py

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Python test](https://github.com/YuzuRyo61/Misskey.py/actions/workflows/test.yml/badge.svg)](https://github.com/YuzuRyo61/Misskey.py/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/YuzuRyo61/Misskey.py/branch/main/graph/badge.svg?token=97A1HJHUMW)](https://codecov.io/gh/YuzuRyo61/Misskey.py)
[![Documentation Status](https://readthedocs.org/projects/misskeypy/badge/?version=latest)](https://misskeypy.readthedocs.io/ja/latest/?badge=latest)

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

mk = Misskey("misskey.io")  # Input instance address (If leaved no attribute, it sets "misskey.io")

# Let's note!
mk.notes_create(
    text="Hello Misskey.py!"
)
```

#### Use token key

```python
from misskey import Misskey

# If use the token
mk = Misskey("misskey.io", i="abcdef123...")
```

### Create token

```python
from misskey import Misskey, MiAuth

auth = MiAuth("misskey.io", name="misskey.py")
# Get Authentication URL, then send to client browser
url = auth.generate_url()
# After permission granted, run this function
token = auth.check()
# To use misskey.py with created token, please below
misskey = Misskey("misskey.io", i=token)  # or: misskey = misskey("misskey.io", i=auth.token)
```

## Other

**Pull requests are HUGE WELCOME!**

We hope you will contribute to the completion of the library by all means.

# Donation

We are accepting at [GitHub Sponsors](https://github.com/sponsors/YuzuRyo61)!

## Donors

- [tearaikazuki](https://github.com/tearaikazuki)

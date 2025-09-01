# alnfile

[![License](https://img.shields.io/pypi/l/alnfile.svg?color=green)](https://github.com/davidetorre99/alnfile/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/alnfile.svg?color=green)](https://pypi.org/project/alnfile)
[![Python Version](https://img.shields.io/pypi/pyversions/alnfile.svg?color=green)](https://python.org)
[![CI](https://github.com/davidetorre99/alnfile/actions/workflows/ci.yml/badge.svg)](https://github.com/davidetorre99/alnfile/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/davidetorre99/alnfile/branch/main/graph/badge.svg)](https://codecov.io/gh/davidetorre99/alnfile)

A Python package for reading AreTomo alignment files into pandas DataFrames.

## Development

The easiest way to get started is to use the [github cli](https://cli.github.com)
and [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
gh repo fork davidetorre99/alnfile --clone
# or just
# gh repo clone davidetorre99/alnfile
cd alnfile
uv sync
```

Run tests:

```sh
uv run pytest
```

Lint files:

```sh
uv run pre-commit run --all-files
```

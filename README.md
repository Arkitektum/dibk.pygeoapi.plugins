# dibk.pygeoapi.plugins

Provider and formatter plugins for [pygeoapi](https://pygeoapi.io), developed
for DiBK. Each plugin is its own Python package with its own version, kept
together in one [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/).

| Package | Directory | Kind |
| --- | --- | --- |
| `postgresql_ext` | [`packages/postgresql_ext`](packages/postgresql_ext) | Feature provider (PostgreSQL) |
| `mvt_postgresql_ext` | [`packages/mvt_postgresql_ext`](packages/mvt_postgresql_ext) | Tile provider (MVT from PostgreSQL) |
| `styles_provider` | [`packages/styles_provider`](packages/styles_provider) | Styles provider |
| `pygeoapi-formatter-jsonfg` | [`packages/jsonfg`](packages/jsonfg) | Output formatter (JSON-FG) |
| `pygeoapi-formatter-gml-npad` | [`packages/gml_npad`](packages/gml_npad) | Output formatter (SOSI-GML NPAD) |

## Installation

The plugins are not published to PyPI. Install them from git, pinned to a
release tag, with `#subdirectory=` pointing at the package:

```dockerfile
RUN uv pip install \
    "postgresql_ext @ git+https://github.com/Arkitektum/dibk.pygeoapi.plugins@postgresql_ext-v0.5.3#subdirectory=packages/postgresql_ext" \
    "pygeoapi-formatter-gml-npad @ git+https://github.com/Arkitektum/dibk.pygeoapi.plugins@gml_npad-v0.5.1#subdirectory=packages/gml_npad"
```

`pip install` takes the same requirement strings.

## Releases

Each package is released on its own. A release tag is the package's directory
name and its version, `<directory>-v<version>`:

1. Bump `version` in `packages/<directory>/pyproject.toml`.
2. Commit, then tag: `git tag postgresql_ext-v0.5.3`.
3. Push the tag and update the pin in the consuming Dockerfile.

Tags from before the plugins were merged into this repository (`v0.5.2` etc.)
only exist in the original, archived repositories.

## Development

```bash
uv sync --all-packages          # all plugins plus dev tools, one shared .venv
uv run ruff check .
uv run pytest packages/gml_npad # run tests one package at a time
```

Run tests per package: each package has its own pytest configuration, and
`postgresql_ext` stubs `osgeo` while `jsonfg` needs the real GDAL bindings, so
they cannot share one pytest process.

`jsonfg` tests and `postgresql_ext` at runtime need GDAL. Install the system
libraries first (`apt-get install libgdal-dev gdal-bin` on Ubuntu), then
`uv pip install "gdal==$(gdal-config --version)"`.

The `gml_npad` smoke tests need a running PostGIS; see
[`packages/gml_npad/tests/smoke/conftest.py`](packages/gml_npad/tests/smoke/conftest.py)
and run them with:

```bash
uv sync --all-packages --extra smoke
uv run pytest packages/gml_npad -m smoke
```

# dibk_pygeoapi_plugins

Stable `dibk.pygeoapi.plugins.*` names for the DiBK pygeoapi plugins, for use
as `name:` in the pygeoapi config:

| `name` | Kind | Implemented by |
| --- | --- | --- |
| `dibk.pygeoapi.plugins.provider.PostgreSQL` | `feature` provider | `postgresql_provider.PostgreSQLProvider` |
| `dibk.pygeoapi.plugins.provider.MvtPostgreSQL` | `tile` provider | `mvt_postgresql_provider.MVTPostgreSQLProvider` |
| `dibk.pygeoapi.plugins.provider.Styles` | `style` provider | `styles_provider.StyleProvider` |
| `dibk.pygeoapi.plugins.formatter.JsonFG` | formatter | `jsonfg_formatter.JsonFgFormatter` |
| `dibk.pygeoapi.plugins.formatter.reguleringsplan_20190401.Reguleringsplan` | formatter | `gml_npad_formatter.reguleringsplan_20190401.ReguleringsplanFormatter` |
| `dibk.pygeoapi.plugins.formatter.kommuneplan_20190401.Kommuneplan` | formatter | `gml_npad_formatter.kommuneplan_20190401.KommuneplanFormatter` |

The names are aliases, not copies: each one returns the class from the
package in the right-hand column. The configuration options are those of that
package; see its README.

```yaml
resources:
  reguleringsplaner_rpomrade:
    type: collection
    providers:
      - type: feature
        name: dibk.pygeoapi.plugins.provider.PostgreSQL
        # ...
    formatters:
      - name: dibk.pygeoapi.plugins.formatter.reguleringsplan_20190401.Reguleringsplan
        feature_type: RpOmråde
```

## Installation

This package has no dependencies. Install it next to the plugins the
deployment uses; a name only imports its plugin package when pygeoapi looks it
up, so plugins that are not configured do not need to be installed:

```bash
uv pip install \
    "dibk_pygeoapi_plugins @ git+https://github.com/Arkitektum/dibk.pygeoapi.plugins@dibk_pygeoapi_plugins-v<version>#subdirectory=packages/dibk_pygeoapi_plugins" \
    "postgresql_provider @ git+https://github.com/Arkitektum/dibk.pygeoapi.plugins@postgresql_provider-v<version>#subdirectory=packages/postgresql_provider"
```

Looking up a name whose plugin is not installed raises `ModuleNotFoundError`
naming the missing package.

`dibk` and `dibk.pygeoapi` are namespace packages, so other distributions can
add their own `dibk.*` packages alongside this one.

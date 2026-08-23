# Uber Base / Base Web source of truth

The complete upstream [Uber Base Web](https://github.com/uber/baseweb) system is pinned at `vendor/baseweb/` as a Git submodule. It includes Base Web's literal implementation, documentation-site pages, component examples, theme definitions, and source files.

Initialize it after cloning:

```bash
git submodule update --init --recursive
python3 scripts/index_base_web_source.py
```

`fern/data/design-systems/base-web/source-index.json` identifies every documentation and implementation file by path and SHA-256. The index is a provenance map; the actual Base content remains in the upstream-pinned source tree.

The Fern site is not a React runtime, so Base Web components cannot be mounted directly inside Fern MDX. The implementation work must therefore map Base's literal theme tokens, component states, sizing, typography, and grid semantics to the Fern rendering layer—without inventing a parallel semantic system.

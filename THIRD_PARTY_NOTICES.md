# VEYRA third-party dependency and licensing inventory

This is a Phase 0 template. Complete and review it before distribution.
Package licenses do not automatically cover native libraries, model files,
fonts, icons, or other bundled assets.

| Component | Exact version | Type | License | Source URL | License/notice URL | Bundled? | Review status |
|---|---|---|---|---|---|---|---|
| PySide6 | 6.8.2 | Runtime package | TODO | https://pypi.org/project/PySide6/ | TODO | TODO | Verify Qt licensing and notices |
| opencv-python | 4.10.0.84 | Runtime camera capture | TODO | https://pypi.org/project/opencv-python/ | TODO | TODO | Review OpenCV and bundled native DLL notices |
| setuptools | 75.8.0 | Build dependency | TODO | https://pypi.org/project/setuptools/ | TODO | No | Verify at build time |
| pytest | 8.3.5 | Development-only | TODO | https://pypi.org/project/pytest/ | TODO | No | Development only |
| pytest-cov | 6.0.0 | Development-only | TODO | https://pypi.org/project/pytest-cov/ | TODO | No | Development only |
| ruff | 0.9.7 | Development-only | TODO | https://pypi.org/project/ruff/ | TODO | No | Development only |

## Future model and native asset inventory

| Asset | Version/hash | License | Model card/source | Redistribution allowed? | Required notices | Review status |
|---|---|---|---|---|---|---|
| No model selected | N/A | N/A | N/A | N/A | N/A | Phase 3 decision required |

## Review checklist

- [ ] Confirm exact installed versions and transitive dependencies.
- [ ] Record license text and required attribution for every distributed component.
- [ ] Review PySide6/Qt licensing for the intended distribution model.
- [ ] Record licenses for native DLLs bundled by packaging tools.
- [ ] Record model cards, hashes, training-data terms, and redistribution rights.
- [ ] Have legal/compliance review completed before public distribution.


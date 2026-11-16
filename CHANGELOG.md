# Changelog

All notable changes to pynotebook and pnb are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.4.2] - 2026-11-16

### Added
- pnb: File → Open Recent, shared by all windows.
- pnb: Help → Demos opens the example notebooks; Help → About pnb shows the versions.

### Changed
- The example notebooks are part of the pnb package, so pip installs them too. The Linux packages now install them to `/usr/share/pnb/pnb/examples/`.

### Fixed
- Cursor up/down did not leave the current cell.
- pnb showed no icon in the GNOME Alt-Tab switcher (Wayland).

## [0.4.1] - 2026-11-14

### Fixed
- Return inserted several lines (and code cells lost their indentation) in notebooks with more than one cell.
- Paragraph styles in text cells were not found in notebooks with more than one cell.

## [0.4.0] - 2026-11-14

### Added
- Linux packages (`.deb`, `.rpm`) for pnb; they use the wxPython of the distribution, so nothing has to be built.
- Automatic builds: tests on every push; for a version tag, Linux packages and the upload of pynotebook and pnb to PyPI.
- Desktop integration for pnb on Linux: menu entry, icon, opening `.pnb` files.
- Indent and dedent (Ctrl-I / Ctrl-U).
- Blinking cursor.
- `python all_tests.py` runs all tests and fails if a test fails.

### Changed
- New default file format: notebooks are saved as readable JSON. It is as safe as before: only known classes are loaded, opening a file never runs code. Files of older versions are still read.
- cerealizer is only needed to read files of older versions.
- Bitmaps are saved as PNG.
- Text model and text view are shared with [MiniWord](https://codeberg.org/chrisecker/miniword): new layout and line wrap, drawing with `wx.GraphicsContext`, fixes for high DPI screens.
- Help on the word at the cursor: Ctrl-H instead of F1.
- Improved text style inspector.
- Packaging with `pyproject.toml` instead of `setup.py`; Python 3.10 or newer.
- Dependencies are declared: cerealizer; wxPython 4.2 or newer as optional extra (`pip install "pnb[wx]"`), since on Linux the wxPython of the distribution is usually preferred.
- READMEs and screenshots updated.

### Fixed
- Copy did not reach the system clipboard (Ubuntu, wxPython 4.2.2).
- Instabilities when deleting to the end of a line.
- The cursor jumped to a wrong position when clicking right of an input cell.
- Shift+Return behind the last cell gave an error.
- Line wrap; inserting a new line.
- Images could show artefacts after loading a saved notebook.
- Compatibility with matplotlib 3.8 or newer and current wxPython; the 3D plot in the demo was empty.
- Syntax colouring.

### Removed
- Python 2 compatibility code.
- Unused draft of an XML format.

## [0.3.0] - 2023-01-01
- Switched to Python 3.
- Restructured repository.
- Removed "Dot".
- Renamed "Text" to "GraphicsText".
- Better clipboard support (bitmaps).

## [0.2.6] - 2020-08-02
- Works with wxPython 3.0 or newer.
- Removed logging framework.
- Better unicode handling.
- Many bugfixes.

## [0.2.5] - 2018-02-11
- Bugfixes (line wrap, word selection, page width).

## [0.2.4] - 2018-01-01
- Separate releases of pnb and rnb.
- Improved graphics.
- Many bugfixes.

## [0.2.3] - 2017-07-22
- Improved look.
- Simpler and faster editor.

## 0.2.1, 0.2.2 - 2016-11-26
- Fixed some packaging issues.

## 0.2.0 - 2016-11-25
- pnb application.
- Much faster colorization.
- Many bugfixes and improvements.

## 0.1.0 - 2016-07-21
- Rewrote `textmodel/texeltree.py`.
- Implemented TextCell.
- Many bugfixes and improvements.

## 0.0.1 - 2016-03-16
- Initial release.

[Unreleased]: https://codeberg.org/chrisecker/pynotebook/compare/v0.4.2...HEAD
[0.4.2]: https://codeberg.org/chrisecker/pynotebook/compare/v0.4.1...v0.4.2
[0.4.1]: https://codeberg.org/chrisecker/pynotebook/compare/v0.4.0...v0.4.1
[0.4.0]: https://codeberg.org/chrisecker/pynotebook/compare/v0.3.0...v0.4.0
[0.3.0]: https://codeberg.org/chrisecker/pynotebook/compare/v0.2.6...v0.3.0
[0.2.6]: https://codeberg.org/chrisecker/pynotebook/compare/v0.2.5...v0.2.6
[0.2.5]: https://codeberg.org/chrisecker/pynotebook/compare/v0.2.4...v0.2.5
[0.2.4]: https://codeberg.org/chrisecker/pynotebook/compare/v0.2.3...v0.2.4
[0.2.3]: https://codeberg.org/chrisecker/pynotebook/src/tag/v0.2.3

<!-- ---
hide:
  - navigation
---
 -->
# Poetry Import Plugin

`poetry-import-plugin` is a Python plugin for Poetry that simplifies the process of importing dependencies from `requirements.txt` files into a Poetry project. It allows you to integrate dependencies into specified dependency groups within the project's `pyproject.toml` file, optionally applying constraints from a constraints file. This plugin also supports updating the Poetry lock file and installing dependencies.

ps. It is renamed from `Req2Toml`




## Features

- Import dependencies from multiple `requirements.txt` files into specified groups.
- Apply version constraints from a constraints file.



## Installation

Please follow the [official docs](https://python-poetry.org/docs/plugins/#using-plugins) for the latest available methods.

Currently (as of 2024), poetry provides three ways to install the plugin:

#### With `pipx inject`

```bash
# To install
pipx inject poetry-import-plugin

# To uninstall
pipx uninject poetry-import-plugin
```



#### With `pip`

Install from [PyPI](https://pypi.org/project/poetry-import-plugin/)

```bash
# To install
$POETRY_HOME/bin/pip install --no-cache-dir poetry-import-plugin

# To uninstall
$POETRY_HOME/bin/pip uninstall poetry-import-plugin
```



#### The `self add` command (⚠️ not recommended for Windows users)

```bash
# To install
poetry self add poetry-import-plugin

# To uninstall
poetry self remove poetry-plugin
```



## Usage

The `import` command can be used to import dependencies from `requirements.txt` files into your Poetry project. Below are the available options and arguments:

### Arguments

- `files` (optional, multiple): The `requirements.txt` files to import.

### Options

- `--group`, `-g` (optional, multiple): Specifies the dependency group(s) into which the dependencies will be imported. Multiple groups can be specified, each followed by a list of dependency files to import.
- `--constraint`, `-c` (optional): Specifies a constraint file to apply version restrictions on dependencies during import.
- `--lock` (optional): Updates the Poetry lock file without installing the packages.
- `--no-update` (optional): Prevents updating the lock file when running the lock operation.
- `--install` (optional): Runs a Poetry installation to install all dependencies defined in `pyproject.toml`.

### Examples
<br>
1. Import dependencies from `requirements.txt` into the default group:

```bash
poetry import requirements.txt
```
<br>
2. Import dependencies from multiple `requirements.txt` files into specific groups:

```bash
poetry import -g dev dev-requirements.txt -g test test-requirements.txt
```
<br>
3. Apply constraints from a constraints file during import:

```bash
poetry import -c constraints.txt requirements.txt
```

<br>
4. Update the Poetry lock file after importing dependencies:

```bash
poetry import --lock requirements.txt
```

<br>
5. Install all dependencies after importing:

```bash
poetry import --install requirements.txt
```



## Contact

For any questions or feedback, please open an issue on the GitHub repository or contact the author.

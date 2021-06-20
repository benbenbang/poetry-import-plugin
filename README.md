# Req2Toml

Adding the dependencies from `requirements.txt` to `pyproject.toml` and `poetry.lock` with one command 😉



## Install

```bash
$ pip install req2toml
```



## Usages

The entrypoint of the converter is `req2lock`

#### Options

- `-f` [required]  The  path to the `requirements.txt`
- `--install` [optional] By default, it will only update the lock, add this flag to install the dependencies at the same time.
- `--dev` [optional] By default, the flag is disable, pass `--dev` to add packages to dev section.
- `-v`: Enable verbose mode to print out the debug logs



```shell
# Only update the poetry.lock
$ req2lock -f requirements.txt

# Install
$ req2lock -f requirements.txt --install

# To dev
$ req2lock -f requirements_test.txt --install --dev
```



## Contributing

PR is always welcome <3

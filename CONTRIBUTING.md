## Contributing
Make yourself a copy of the project and create your own branch
```shell script
git checkout develop; git pull
git checkout -b "feature-name"
```
### Running tests

You need additional packages in order to run the tests:
```sh
pip install ".[dev]"
```

In order to run the test, you can use the following command:
```sh
python tests/test_eotile.py
```
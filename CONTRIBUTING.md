<!--
Copyright (c) 2021 CS GROUP - France.

This file is part of EOTile.
See https://github.com/CS-SI/eotile for further info.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
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

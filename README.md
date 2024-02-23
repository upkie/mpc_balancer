This template repository makes it easier to create new agents for [Upkie](https://github.com/upkie/upkie) wheeled bipeds.

## Getting started

1. Create a new repository from this template.
2. Search for the string "XXX": it indicates template values to configure, such as the project name.
3. Replace ``LICENSE`` with the license of your choice (the default one is Apache-2.0)
4. Implement your agent in the ``agent`` directory.
5. Optional: adapt the spines in the ``spines`` directory, for instance with custom observers.

## Usage

The `Makefile` can be to build and upload your agent to the real robot. Run ``make help`` for a list of available rules.

You can also run your agent locally with Bazelisk:

```bash
$ ./tools/bazelisk run //agent
```

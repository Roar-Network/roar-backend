# Contributing to Roar

The following is a set of guidelines for contributing to Roar Backend , which are hosted in the Roar Organization on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check all the opened issues may be you don't need to create new one. When you are creating a bug report, please include as many details as possible. Fill out [the required template](https://github.com/Roar-Network/roar-backend/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D), the information it asks for helps us resolve issues faster.

**Note:** If you find a Closed issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

### Suggesting Enhancements

Before suggesting enhacements, please check all the opened issues may be someone suggest this enhacemnet before you. Fill out [the required template](https://github.com/Roar-Network/roar-backend/issues/new?assignees=&labels=enhacement&template=feature_request.md&title=%5BFEATURE%5D), the information it asks for help us implement enhacement faster.

**Note:** If a new enhacement is suggested by someone, discuss way to implement that, and pro & cons. 

## Pull requests

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template]()
2. Follow [the styleguides](#styleguides)
3. After you submit your pull request, verify that all status checks are passing
    - What if the status checks are failing? If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe the failure is unrelated. A maintainer will re-run the status check for you. If we conclude that the failure was a false positive, then we will open an issue to track that problem with our status check suite.

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

- Follow PEP8 styles
- When commit, follow commit message guide:
    - The structure of a message is:
        ```
            <id> - Title

            Description
        ```
    - `<id>` is an emoji of the type of commit, by example:
        - 🆕 new feature
        - 🔧 bug fixed
        - 📖 documentation
        - 🧪 tests
        - 🎨 style, formatting, refactoring
    - In Title use only imperative like 'change' not 'changed'. Be short & don't write useless titles like 'take Juan, I fix all'.
    - In Description use imperatives. Be descriptive & short. 

### Example of commit

```
🎨 - Refactor main.py

Change App class, remove all useless lines, refactor imports.
```
        
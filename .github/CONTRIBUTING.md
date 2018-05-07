# Contributing to ABE

:+1::tada: First off, thanks for taking the time to contribute to ABE! :tada::+1:

The following is a set of guidelines for contributing to ABE.
These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Styleguides

### Python Styleguide

New code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
and [PEP 257](https://www.python.org/dev/peps/pep-0257/).
Run `pipenv run flake8 abe` to check your code.
Old code doesn't follow these guidelines, so you'll see a lot of noise.

### Markdown Styleguide

Markdown should pass [markdown-lint](https://github.com/remarkjs/remark-lint).

The following editor plugins keep code in compliance with markdown-lint:

* Atom: [linter-markdown](https://atom.io/packages/linter-markdown)
* Visual Studio Code:
  * [markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
    lints Markdown files.
  * [remark](https://marketplace.visualstudio.com/items?itemName=mrmlnc.vscode-remark)
    beautifies Markdown files.

## Acknowledgements

Portions of this guide were adapted from the [Atom contribution guide](https://github.com/atom/atom/blob/master/CONTRIBUTING.md#styleguides).

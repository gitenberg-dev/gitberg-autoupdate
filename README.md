# Gitberg-autoupdate
[GITenberg](https://gitenberg.org/) is a project to collectively curate ebooks on GitHub.
[Gitberg](https://github.com/gitenberg-dev/gitberg) is a command line tool to automate tasks on books stored in git repositories.
[Gitberg-autoupdate](https://github.com/gitenberg-dev/gitberg-autoupdate) is a set of automated tools to continuously update
GITenberg.


### Config

Some commands require a config file before they can be used.
See [gitberg's documentation](https://github.com/gitenberg-dev/gitberg/#config)
for details.

### Development

To run project in development mode clone the project and do:

    python setup.py develop

The following environment variables must be set to the appropriate values:
  * `GITHUB_WEBHOOK_SECRET`
  * `AWS_DEFAULT_REGION`
  * `AWS_ACCESS_KEY_ID`
  * `AWS_SECRET_ACCESS_KEY`

## Testing

To run project tests do:

    python setup.py test

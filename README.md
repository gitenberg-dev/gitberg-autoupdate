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

## Deployment

Both servers run in an AWS Elastic Beanstalk (EBS) application. `webhook_server`
runs as a "Web server environment", and `autoupdate_worker` runs as a
"Worker environment".

Configure the following environment variables (under Configuration > Software > Environment properties) for `webhook_server` environments:
  * `GITHUB_WEBHOOK_SECRET`
  * `AWS_DEFAULT_REGION`
  * `GITENBERG_SECRET`
  * `GITBERG_GH_USER`
  * `GITBERG_GH_PASSWORD`
  * `SSH_KEY_PASSWORD` (this is the password to `deploy/autoupdate_worker/id_rsa_password`)
  * Note that you *must* set these *all* when first creating the environment.
    Otherwise, it won't start and is then apparently unrecoverable.
  * Don't set `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`. The EBS instance
    role will be picked up automatically instead.

The EBS environment must be configured as follows for `webhook_server` environments:
  * Virtual machine instance profile: elasticbeanstalk-ec2-autoupdate
  * Health check path (under Monitoring): `/health`
  * Environment type: load balancing
  * Load balancer: add a HTTPS listener on 443 which delivers to HTTP on 80, using an appropriate SSL certificate

Configure the following environment variables (under Configuration > Software > Environment properties) for `autoupdate_worker` environments:
  * `GITENBERG_SECRET`

The EBS environment must be configured as follows for `autoupdate_worker` environments:
  * Virtual machine instance profile: elasticbeanstalk-ec2-autoupdate
  * Health check path (under Monitoring): `/health`
  * Environment type: load balancing
  * HTTP path (under Worker): `/do_update`
  * Worker queue (under Worker): gitberg-autoupdate-repositories
  * HTTP connections (under Worker): 5
  * Visibility timeout (under Worker): 600

Create the deployment zips using
    `python deploy/make_deploy.py webhook_server`
and 
    `python deploy/make_deploy.py autoupdate_worker`
then upload to EB application versions. Make sure to commit your changes first.

### Local mock deployment

To run one of the servers locally in a Docker container identical to the one
which will be used by EBS, use these commands:
```console
$ docker build -f deploy/webhook_server/Dockerfile -t webhook_server ./ && docker run -i --env-file test_env -p 127.0.0.1:1234:80 webhook_server
$ docker build -f deploy/autoupdate_worker/Dockerfile -t autoupdate_worker ./ && docker run -i --env-file test_env -p 127.0.0.1:1235:80 autoupdate_worker
```

These commands rely on a file called `test_env` with the environment variables
specified above under [Development](#development) to be configured.

#### Testing in Development

You can use ngrok https://ngrok.com/ to send a github webhook to the auto-update server - it will put events on the configured queuing service.

To test the local autoupdate worker, just send it a post with curl, for example
```curl --data "GITenberg/Relativity-the-Special-and-General-Theory_5001 0.1.2" http://127.0.0.1:1235/do_update
```
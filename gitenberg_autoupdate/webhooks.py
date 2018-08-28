import logging
import os
import requests

GITENSITE_YAML_URL = "https://gitenberg.org/books/post/"
# header: x-gitenberg-secret
GITENBERG_SECRET = os.environ['GITENBERG_SECRET']
UNGLUEIT_URL = "https://unglue.it/api/travisci/webhook"

def gitensite(book):
    headers = {'x-gitenberg-secret': GITENBERG_SECRET}
    response = requests.post(GITENSITE_YAML_URL, book.meta.__unicode__(), headers=headers)
    logging.info('Got from gitensite: %s' % response)
    return response.ok

def unglueit(book):
    payload = {'status_message': 'Passed', 'type': 'push'}
    payload['owner_name'] = book.github_repo.org_name
    payload['name'] = book.repo_name
    response = requests.post(UNGLUEIT_URL, json={'payload': payload})    
    logging.info('Got from unglueit: %s' % response)
    return response.ok

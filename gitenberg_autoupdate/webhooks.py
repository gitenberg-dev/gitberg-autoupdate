import json
import logging
import os
import requests

GITENSITE_YAML_URL = "https://gitenberg.org/books/post/"
# header: x-gitenberg-secret
GITENBERG_SECRET = os.environ['GITENBERG_SECRET']
UNGLUEIT_URL = "https://unglue.it/api/travisci/webhook"

def gitensite(book):
    headers = {'x-gitenberg-secret': GITENBERG_SECRET}
    response = requests.post(GITENSITE_YAML_URL, json=book.meta.metadata, headers=headers)
    logging.info('Got from gitensite: %s' % response)
    return response.status_code == 200

def unglueit(book):
    repository = {}
    repository['owner_name'] = book.github_repo.org_name
    repository['name'] = book.repo_name
    payload = {'status_message': 'Passed', 'type': 'push', 'repository':repository}
    try:
        response = requests.post(UNGLUEIT_URL, data={'payload': json.dumps(payload)})
    except ConnectionError as ce:
        time.sleep(60)
        try:
            response = requests.post(UNGLUEIT_URL, data={'payload': json.dumps(payload)})
        except ConnectionError as ce2:
            logging.error(ce2)
            return False
    logging.info('Got from unglueit: %s' % response)
    return response.status_code == 200

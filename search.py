from github import Github
import requests
import base64
import yaml
from pymongo import MongoClient

db = MongoClient().pypo

search_text = input('What would you like to search for?')


def already_exists(repository):
    return db.pypo.find({'repo_name': '{}'.format(repository)}).count() > 0


if search_text != '':

    with open("settings.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)

    results = g.search_repositories('"{}+ "+in:readme'.format(search_text))

    print('there are %d total results' % results.totalCount)

    string_match = '{}'.format(search_text)

    regex_string = '^.*%s\s.*$' % (string_match)

    for repo in results:

        if not(already_exists(repo.full_name)):

            print('{} being added...'.format(repo.full_name))

            r = requests.get(repo.html_url)
            if r.headers.get('status') is not int(404):
                print('url is ', repo.html_url)

                readme = repo.get_readme()
                data = base64.b64decode(readme.content)

                result = db.pypo.insert_one({
                    "url": repo.html_url,
                    "repo_id": repo.id,
                    "repo_name": repo.full_name,
                    "pull_request_submitted": False,
                    "pull_request_merged": False,
                    "pull_request_number": 0,
                    "forks_deleted": False,
                    "search_text": search_text,
                    "fullText": data
                })
                print("Saved [{}].".format(result.inserted_id))
                print('\n\n\n\n')

        else:
            print('already found {}, skipping...'.format(repo.full_name))

    print('\n\n\nall done!')

else:
    print('alright, nevermind then...')

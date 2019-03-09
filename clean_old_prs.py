from github import Github
from pymongo import MongoClient
import os
import shutil
import time
import yaml

FORK_ROOT = 'forks/'

with open('settings.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

def get_mongo_name(url):
    # hack to grab repo syntax for mongo
    end_index = url.find('/issues')
    return url[29:end_index]

def get_rate_limit(g):
    limit = g.get_rate_limit()
    return limit.core.remaining

# connect to mongo and github
db = MongoClient().pypo
g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)

'''
we probably want to delete local file-system repos for PRs that are older than a month or so...
iterate through the MongoDB record (ID's should translate to datetime stamps)
and keep the remote fork, but delete the local files
'''




# find all merged PRs by the user
issues = g.search_issues(query='', **{'type':'pr', 'is':'merged', 'author':cfg['user']})

for issue in issues:
    remaining = get_rate_limit(g)
    if (remaining < 250):
        print('rate limit low...sleeping...')
        time.sleep(60)
    repo_full_name = get_mongo_name(issue.url)
    other_user, project_name = repo_full_name.split('/')

    # checking mongo to see if already processed
    record = db.pypo.find_one({'repo_name': repo_full_name})
    if (other_user is not 'lpmi-13'):

        # deleting remote repo fork
        print('\n\ndeleting remote fork for {}...'.format(repo_full_name))
        try:
            remote_repo = g.get_repo('{}/{}'.format(cfg['user'], project_name))
            remote_repo.delete()
        except:
            print('remote fork already deleted')
           
        # delete the local fork on disk
        print('deleting the local fork on disk for {}'.format(repo_full_name))
        local_repo = os.path.join(FORK_ROOT, '{}'.format(other_user))
        if os.path.isdir(local_repo):
            shutil.rmtree(local_repo)
        else:
            print('already deleted...')
    
        # update the record in mongo
        print('updating record in mongo to pull_request_merged: True')
        db.pypo.update({'repo_name': repo_full_name}, { '$set' : { 'pull_request_merged' : True , 'forks_deleted': True } })
    else:
        print('already processed {}, continuing...'.format(repo_full_name))

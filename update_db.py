import shutil
from github import Github
from pymongo import MongoClient
import yaml

print 'Checking DB for PRs that have been merged...'

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

db = MongoClient().pypo
g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)
# get a list of the PRs that have been submitted
documents = db.pypo.find({'pull_request_submitted':True})
for document in documents:

    #not current working, because needs to be repo_id
    repo = g.get_repo(document['repo_name'])
    pull_request = repo.get_pull(document['pull_request_number'])
    merged_status = pull_request.merged

    #if PR has been approved/closed, then remove the local directory, as well as the remote repo on github
    if (merged_status == True):

        #remove remote fork
        repository = g.get_repo(document['repo.id'])
        repository.delete()

        print 'remote fork of {} deleted'.format(document['url'])
        #remove local directory and delete fork on Github
        directory_path = 'forks/' + document['repo_name']
        shutil.rmtree(directory_path, ignore_errors=True)

        print 'local file directory {} deleted'.format(directory_path)

print 'Update complete!'

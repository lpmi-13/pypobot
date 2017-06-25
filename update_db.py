from github import Github
import git, shutil
from pymongo import MongoClient
import yaml

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

db = MongoClient().pypo
g = GitHub(cfg['user'], cfg['password'], timeout=200, per_page=30)

#checks if a pull request has already been submitted for repo
def already_submitted(repo_id):
    documents = db.pypo.find_one({'repo_id':repo.id, 'pull_request_submitted': True})
    if len(documents) > 0:
        return True
    else:
        return False

#checks if the pull request has already been merged
def check_request_status(repo_id, pull_number):
    repo = g.get_repo(repo_id)
    pull_request = repo.get_pull(pull_number)

    return pull_request.merged == True

#for all pull requests that have been approved, remove from file system and remote repo
def clear_already_merged():

    # get a list of the PRs that have been submitted
    documents = db.pypo.find().filter({'pull_request_submitted':True})
    for document in documents:

        #access the online repo by repo_id and check status of PR
        merged_status = check_request_status(document['repo_id'], document['pull_request_number'])

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


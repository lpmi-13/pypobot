from fileparser import parsefile
from github import Github
from pymongo import MongoClient
import git
import os
import re
import requests
import shutil
import yaml

# these are hardcoded for now but will eventually be procedurally generated
FORM = ' an an '
CORRECTION_FORM = ' an '

pattern = re.compile(FORM)

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

db = MongoClient().pypo
g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)
# grab the user to create a fork later
user = g.get_user()

response = input('Would you like to see the first suggested correction? (y/n)')

if (response == 'y'):
    documents = db.pypo.find()
    for item in documents:

        # checks if this particular typo already has a pull request submitted. If so, skipped.
        if (item['pull_request_submitted'] is True):
            continue
        elif (item['repo_id'] is None):
            continue
        else:

            typo_lines = []
            text = item['fullText'].decode('utf-8')

            for line in text.splitlines():
                if(pattern.search(line)):
                    typo_lines.append(line)

            if (len(typo_lines) > 0):

                original = typo_lines[0]
                suggestion = original.replace('{}'.format(FORM), '{}'.format(CORRECTION_FORM))
                print('looking at {}\n\n'.format(item['url']))
                print('-------------------- original:\n', original, '\n\n--------------- suggested fix:\n ', suggestion, '\n\n')
                response = input('Would you like to correct this? (y/n)')
                if (response == 'y'):
                    print('grabbing repo at %s ...' % (item['url']))
                    result = g.get_repo(item['repo_id'])
                    repo_name = result.full_name
                    repo_owner = result.owner.login
                    default_branch = result.default_branch

                    print('creating remote fork for %s ...' % (item['url']))

                    forked = user.create_fork(result)

                    DIR_ROOT = 'forks/'
                    FULL_PATH = os.path.join(DIR_ROOT, repo_name)
                    REMOTE_URL = forked.ssh_url

                    if os.path.isdir(FULL_PATH):
                        shutil.rmtree(FULL_PATH)
                    os.makedirs(FULL_PATH)

                    local_repo = git.Repo.init(FULL_PATH)
                    origin = local_repo.create_remote('origin', REMOTE_URL)

                    print('cloning local copy of fork in %s' % (FULL_PATH))

                    try:
                        origin.fetch()
                        origin.pull(refspec='{}'.format(default_branch))

                        indexOfRepoName = local_repo.working_dir.rfind('/')
                        local_repo_name = local_repo.working_dir[indexOfRepoName:]

                        new_branch_name = 'typofix'
                        print('creating new feature branch %s for %s' % (new_branch_name, FULL_PATH))
                        new_branch = local_repo.create_head(new_branch_name)
                        local_repo.heads.typofix.checkout()

                        # this is just because README files can have random file names/extensions
                        api_response = requests.get('https://api.github.com/repos/' + repo_name + '/readme')

                        repoInfo = api_response.json()

                        readmeFile = repoInfo['name']

                        pathToReadmeFile = os.path.join(FULL_PATH, readmeFile)

                        print('found readme at {}'.format(pathToReadmeFile))

                        newFileArray = []

                        try:
                            with open(pathToReadmeFile) as readme:
                                for line in readme:
                                    newFileArray.append(line)
                            # this is where we loop through all the places the error occurs
                            revised_array = parsefile(newFileArray, FORM, CORRECTION_FORM)

                            # this takes the full updated readme and writes it to the file
                            with open(pathToReadmeFile, 'w') as new_readme:
                                for line in revised_array:
                                    new_readme.write(line)

                            print('adding new README and committing to the ' + new_branch_name + ' branch')

                            updatedReadmePath = os.path.join(local_repo.working_tree_dir, readmeFile)

                            local_repo.index.add([updatedReadmePath])
                            local_repo.index.commit('fix simple typo')

                            print('pushing back changes to remote fork')
                            try:

                                origin.push(refspec='{}'.format(new_branch_name))
                            except:

                                local_repo.remotes.origin.pull(refspec='{}'.format(default_branch))
                                origin.push(refspec='{}'.format(new_branch_name))
                            print('creating pull request from new branch')

                            try:

                                record_to_update = db.pypo.update({'repo_name': item['repo_name']}, {'$set': {'pull_request_submitted': True}})
                            except:

                                print('Test Complete')
                                print('\n\n\n')

                        except:
                            print('unable to find/update readme')
                            continue

                    except:
                        print('unable to clone repo')
                        continue
else:
    print('okay, nevermind')

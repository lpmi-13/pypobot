from github import Github
from pymongo import MongoClient
import git, os, shutil, requests, time
import yaml,json
from fileparser import parsefile
from update_db import clear_already_merged

from loggerPrefs import prefs

prefs()

be_aux_forms = [
    'be', 'is', 'are', 'am', 'was', 'were', 'being', 'been'
]

#these are hardcoded for now but will eventually be procedurally generated
FORM = 'send'
CORRECTION_FORM = 'sent'

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

db = MongoClient().pypo
g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)
user = g.get_user()


print 'checking for merged PRs and updating DB...'

clear_already_merged(g, db)

import pdb;pdb.set_trace()

response = raw_input('Would you like to see the first suggested correction? (y/n)')


if (response is 'y'):
    documents = db.pypo.find()
    for item in documents:

        # checks if this particular typo already has a pull request submitted. If so, skipped.
        if (item['pull_request_submitted'] == True):
            continue
        else:
    
            original = item['line']
            suggestion = item['line'].replace(' {}'.format(FORM), ' {}'.format(CORRECTION_FORM))
            print 'looking at {}\n\n'.format(item['url'])
            print '-------------------- original:\n',item['line'],'\n\n--------------- suggested fix:\n ', suggestion,'\n\n'
            response = raw_input('Would you like to correct this? (y/n)')
            if (response is 'y'):
                print 'grabbing repo at %s ...'%(item['url'])
                result = g.get_repo(item['repo_id'])
                repo_name = result.full_name
                repo_owner = result.owner.login
                default_branch = result.default_branch
    
                print 'creating remote fork for %s ...'%(item['url'])
    
                forked = user.create_fork(result)
    
                DIR_ROOT = 'forks/'
                FULL_PATH = DIR_ROOT + repo_name
                REMOTE_URL = forked.ssh_url
    
                if os.path.isdir(FULL_PATH):
                    shutil.rmtree(FULL_PATH)
                os.makedirs(FULL_PATH)
    
                local_repo = git.Repo.init(FULL_PATH)
                origin = local_repo.create_remote('origin', REMOTE_URL)
    
                print 'cloning local copy of fork in %s'%(FULL_PATH)
    
                try:
                    origin.fetch()
                    origin.pull(refspec='{}'.format(default_branch))
    
                    indexOfRepoName = local_repo.working_dir.rfind('/')
                    local_repo_name = local_repo.working_dir[indexOfRepoName:]
    
                    new_branch_name = 'typofix'
                    print 'creating new feature branch %s for %s'%(new_branch_name, FULL_PATH)
                    new_branch = local_repo.create_head(new_branch_name)
                    local_repo.heads.typofix.checkout()
    
                    #this is just because README files can have random file names/extensions
                    api_response = requests.get('https://api.github.com/repos/' + repo_name + '/readme')
    
    
                    repoInfo = api_response.json()
    
                    readmeFile = repoInfo['name']
    
                    pathToReadmeFile = FULL_PATH + '/' + readmeFile
    
                    print 'found readme at {}'.format(pathToReadmeFile)
    
                    newFileArray = []
    
                    try:
                        with open(pathToReadmeFile) as readme:
                            for line in readme:
                                newFileArray.append(line)
                        #this is where the loop through all auxiliary forms happens
                        revised_array = parsefile(newFileArray, be_aux_forms, FORM, CORRECTION_FORM)
    
                        #this takes the full updated readme and writes it to the file
                        with open(pathToReadmeFile, 'w') as new_readme:
                            for line in revised_array:
                                new_readme.write(line)
    
                        print 'adding new README and committing to the ' + new_branch_name + ' branch'
    
                        updatedReadmePath = os.path.join(local_repo.working_tree_dir, readmeFile)
    
                        local_repo.index.add([updatedReadmePath])
                        local_repo.index.commit('fix simple typo')
    
    
                        print 'pushing back changes to remote fork'
                        try:
        
                            origin.push(refspec='{}'.format(new_branch_name))
                        except:
        
                            local_repo.remotes.origin.pull(refspec='{}'.format(default_branch))
                            origin.push(refspec='{}'.format(new_branch_name))
                        print 'creating pull request from new branch'
    
                        #attempts to submit a pull request for the changes
                        try:
                            pull_request = result.create_pull(title='typo fix', body='fix simple typo', base='{}'.format(default_branch), head='lpmi-13:{}'.format(new_branch_name))
                            #if successful, updates the record in the database
                            record_to_update = db.pypo.update_one({'repo_name': item['repo_name']}, { '$set' : { 'pull_request_submitted' : True ,  'pull_request_number' : pull_request.number}})
    
                        except:
                            import pdb;pdb.set_trace()
        
                        print 'README has been updated!'
        
    #                    print 'Test Complete'
                        print '\n\n\n'
        
        
                    except:
                        print 'unable to find/update readme'
                        continue
    
                except:
                    print 'unable to clone repo'
                    continue
else:
    print 'okay, nevermind'

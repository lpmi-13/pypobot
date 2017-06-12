from github import Github
from pymongo import MongoClient
import git, os, shutil, re, requests, time
import yaml

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

db = MongoClient().pypo
g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)
user = g.get_user()

response = raw_input('Would you like to see the first suggested correction? (y/n)')


if (response is 'y'):
    documents = db.pypo.find()
    for item in documents:
        original = item['line']
        suggestion = item['line'].replace(' send', ' sent')
        print '-------------------- original:\n',item['line'],'\n\n--------------- suggested fix:\n ', suggestion,'\n\n'
        response = raw_input('Would you like to correct this? (y/n)')
        if (response is 'y'):
            #correction_set = db.pypo.find({ 'url' : item['url'] }, { 'line' : 1 })

            print 'grabbing repo at %s ...'%(item['url'])
            result = g.get_repo(item['repo_id'])
            repo_name = result.full_name
            repo_owner = result.owner.login

            print 'creating remote fork for %s ...'%(item['url'])
           # print 'repository id:%s'%(item['repo_id'])

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

#            try:
            origin.fetch()
            origin.pull(origin.refs[0].remote_head)


            new_branch_name = 'typofix'
            print 'creating new feature branch %s for %s'%(new_branch_name, FULL_PATH)
            new_branch = local_repo.create_head(new_branch_name)
            local_repo.heads.typofix.checkout()

            string_to_match = 'be send'
            regex_string = '^.*%s\s.*$' % (string_to_match)

            r = requests.get('https://api.github.com/repos/' + repo_name + '/readme')

            result = r.json()

            readmeFile = result['name']

            pathToReadmeFile = FULL_PATH + '/' + readmeFile

            print "readme filename is " + readmeFile
            print "repo owner is " + repo_owner

            newFileArray = []

            with open(pathToReadmeFile) as readme:
                for line in readme:
                    newFileArray.append(line)

            with open(pathToReadmeFile, 'w') as new_readme:
                for line in newFileArray:
                    if (line.find('be send') > -1):
                        found_at = [m.start() for m in re.finditer('be send', line)]

                        #print "found some stuff at " + index
                        #add some funky find/replace logic here

                        suggestion = line.replace('be send', 'be sent',len(found_at))
                        user_input = raw_input('would you like to change: \n\n {}\n\n into \n\n {}\n? (y/n)'.format(line, suggestion))
                        if (user_input is 'y'):
                            line = suggestion
                        else:
                            continue
                        new_readme.write(line)
                    else:
                        new_readme.write(line)

            print 'adding new files and committing to the ' + new_branch_name + ' branch'

            updatedReadmePath = os.path.join(local_repo.working_tree_dir, readmeFile)

            #print 'I think we\'re writing to: ' + updatedReadmePath

            local_repo.index.add([updatedReadmePath])
            local_repo.index.commit('fix simple typo')

            print 'pushing back changes to remote fork'

            origin.push(refspec='{}'.format(new_branch_name))

            print 'creating pull request from new branch'

            #this is supposed to create a pull request in the original repo but is currently not working
            result.create_pull('typo fix', 'fix simple typos', 'master','lpmi-13:{}'.format(new_branch_name))

            print 'README has been updated! TEST COMPLETE'
            print '\n\n\n'

else:
    print 'okay, nevermind'

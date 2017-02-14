from github import Github
import requests, base64, re, yaml
from pymongo import MongoClient

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)

#repo = 'https://github.com/vedmack/feedback_me'
repo_id = 10852497

print 'grabbing repo...'

result = g.get_repo(repo_id)

print result.html_url

print '\n\n...attempting to create fork...'

user = g.get_user()
forked = user.create_fork(result)

print 'all done!'

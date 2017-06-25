from github import Github
import requests, base64, re, yaml
from pymongo import MongoClient

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

db = MongoClient().pypo

g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)

results = g.search_repositories('"is+spend+ "+in:readme')


print 'there are %d total results' % results.totalCount

string_match = 'is spend'

regex_string = '^.*%s\s.*$' % (string_match)

for repo in results:
    r = requests.get(repo.html_url)
    if r.headers.get('status') is not int(404):
        print 'url is ', repo.html_url

        readme = repo.get_readme()
        data = base64.b64decode(readme.content)

        for line in data.splitlines():
            for item in re.findall(regex_string, line):
                print item
                result = db.pypo.insert_one({
                    "url": repo.html_url,
                    "repo_id": repo.id,
                    "line": item,
                    "fullText": data
                })
                print "Saved [{}].".format(result.inserted_id)
        print ('\n\n\n\n')

print '\n\n\nall done!'

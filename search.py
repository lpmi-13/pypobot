from github import Github
import requests, base64, re, yaml

with open("settings.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

g = Github(cfg['user'], cfg['password'], timeout=200, per_page=30)

#for repo in g.get_user().get_repos():
#    print repo.name

#current_limit = g.get_rate_limit()

results = g.search_repositories('"be+send+ "+in:readme')

write_stream = open('results.txt', 'w')
write_stream.truncate()


print 'there are %d total results' % results.totalCount

write_stream.write('there are %d total results' % results.totalCount)
write_stream.write('\n\n')

string_match = 'be send'

#reg_match = re.compile(string_match)

for repo in results:
    r = requests.get(repo.html_url)
    if r.headers.get('status') is not int(404):
#        print repo.html_url, repo.contents_url(), r.headers.get('status') 
        write_stream.write(repo.html_url)
#        size = repo.size
        print 'url is ', repo.html_url
#        print 'size is ', size
#        print 'master branch is ', repo.master_branch
#        print 'homepage is ', repo.homepage
#        print 'default branch is ', repo.default_branch
#        write_stream.write(repo.html_url)
        write_stream.write('\n')
#        write_stream.write(str(size))
#        write_stream.write('\n')
#        write_stream.write(repo.default_branch)
#        write_stream.write('\n')
#        write_stream.write(r.headers.get('status'))
#        write_stream.write('\n\n\n')

#        readme = repo.get_readme()
#        data = base64.b64decode(readme.content)

#        print data
        print ('\n\n\n\n')

print '\n\n\nall done!'

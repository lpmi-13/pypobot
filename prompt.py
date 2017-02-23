from pymongo import MongoClient

db = MongoClient().pypo

response = raw_input('Would you like to see the first suggested correction? (y/n)')

if (response is 'y'):
    documents = db.pypo.find()
    for item in documents:
        original = item['line']
        suggestion = item['line'].replace(' send ', ' sent ')
        print '-------------------- original:\n',item['line'],'\n\n--------------- suggested fix:\n ', suggestion,'\n\n'
        response = raw_input('Would you like to correct this? (y/n)')
        if response == 'y':
            print 'creating pull request for %s'%(item['url'])
            print 'repository id:%s'%(item['repo_id'])
            print 'updating README with %s'%(suggestion)
            print '\n\n\n'
else:
    print 'okay, nevermind'

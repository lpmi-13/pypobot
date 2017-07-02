# pypobot
yo dawg, we herd you like open source. So we open sourced a way for you to easily contribute to open source

This will eventually contain the spacy-enabled module to generate searches, as well as the manner in which things are pushed into the database for display in a web app (possibly?)

Current control flow is as follows:

SEARCH.PY
- send a search query off to the [Github Search API](https://api.github.com/search/repositories?q=tetris+language:assembly&sort=stars&order=desc
) for a given query (eg, "be send")
- retrieve the results and search through the readme for each result
- if the string is found, store identifying information for that repo in the mongo database

PROMPT.PY
- open up the database connection and clean out all the records with submitted pull requests that have already been merged, delete the remote fork, and remove the local copies from the filesystem
- iterate through the remaining items in the database and check if a pull request has already been submitted
- If no PR has been submitted, prompt the user to submit one
- If user selects a change to make, fork the repo
- Clone the repo to the user's local machine
- Open a new feature branch
- Iterate through the local copy of the readme and prompt user to confirm suggested changes (not currently any way to interactively type changes, but that could be added in the future)
- Stage and commit updated readme file
- Push back changes to fork
- Open a pull request with the updated readme
- Update the record in the database to show that a pull request has been submitted

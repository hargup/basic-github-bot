import os
from flask import Flask, request
from github import Github
from github import GithubException

app = Flask(__name__)
g = Github(os.environ['GITHUB_PERSONAL_ACCESS_TOKEN'])

def add_hello_world(repo_name):
    repo = g.get_repo(repo_name)
    default_branch = repo.default_branch

    new_branch_name = "add-hello-world"
    
    # Create a new branch
    try:
        repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=repo.get_branch(default_branch).commit.sha)
    except GithubException:
        print(f'{new_branch_name} Branch already exists, using it')
        
    try:
        # Get and modify the README file in the new branch
        readme = repo.get_contents("README.md", ref=new_branch_name)
        updated_readme = readme.decoded_content.decode('utf-8') + "\n\nHello World\n"
        repo.update_file("README.md", "Add Hello World to README", updated_readme, readme.sha, branch=new_branch_name)
    except:
        # Create a new README file with "Hello World" content
        repo.create_file("README.md", "Initial commit", "Hello World", branch=new_branch_name)

    
    # Create a pull request
    repo.create_pull(title="Add Hello World to README", body="This PR adds 'Hello World' to the README file.", head=new_branch_name, base=default_branch)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_json()
    if payload['action'] == 'labeled':
        issue = payload['issue']
        label = payload['label']
        if label['name'].lower() == 'hello world':
            repo_name = payload['repository']['full_name']
            add_hello_world(repo_name)
    return 'OK', 200

@app.route('/', methods=['GET'])
def home():
    return 'Hello World!', 200

@app.route('/about')
def about():
    return 'About'

if __name__ == '__main__':
    app.run()

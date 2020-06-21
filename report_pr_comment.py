from github import Github
import os
import json

def read_json(filepath):
    """
    Read a json file as a dictionary.
    Parameters
    ----------
    filepath : str
    Returns
    -------
    data : dict
    """
    with open(filepath, 'r') as f:
        return json.load(f)



def add_comment(new_comment):
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))
    event = read_json(os.getenv('GITHUB_EVENT_PATH'))
    branch_label = event['pull_request']['head']['label']  # author:branch
    branch_name = branch_label.split(':')[-1]
    repo = gh.get_repo(event['repository']['full_name'])
    prs = repo.get_pulls(state='open', sort='created', head=branch_label)
    pr = prs[0]

    # check if this pull request has a duplicated comment
    old_comments = [c.body for c in pr.get_issue_comments()]
    if new_comment in old_comments:
        print('This pull request already a duplicated comment.')
        exit(0)

    # add the comment
    pr.create_issue_comment(new_comment)

if __name__ == '__main__':
    add_comment("SageMaker Running...")


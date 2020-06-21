# Original code from 
# https://github.com/harupy/comment-on-pr/blob/master/entrypoint.py
from github import Github
import os
import json
import pandas as pd
import base64
from io import BytesIO


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

    # https://developer.github.com/webhooks/event-payloads/#pull_request
    event = read_json(os.getenv('GITHUB_EVENT_PATH'))
    branch_label = event['pull_request']['head']['label']  # author:branch

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

def update_leaderboard(score, scoreText="Score", 
        leaderboardFile = ".leaderboard.csv", ascending=True):
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))

    # https://developer.github.com/webhooks/event-payloads/#pull_request
    event = read_json(os.getenv('GITHUB_EVENT_PATH'))
    branch_label = event['pull_request']['head']['label']  # author:branch
    sender = event['sender']['login']

    repo = gh.get_repo(event['repository']['full_name'])
    prs = repo.get_pulls(state='open', sort='created', head=branch_label)
    pr = prs[0]

    entry = "#" + str(pr.number) + " by " + sender

    try: # Check if the file exist
        repo.get_contents(leaderboardFile)
    except: 
        repo.create_file(leaderboardFile, "initial commit", scoreText + ", Entity")
        pass
    
    contents = repo.get_contents(leaderboardFile)
    df = pd.read_csv(BytesIO(base64.b64decode(contents.content)))

    df.loc[len(df.index)] =  [score, entry] 

    df = df.sort_values(by=df.columns[0], ascending=False)

    new_leaderbord_content = df.to_csv(index=False)
    repo.update_file(leaderboardFile, "Score added", 
        new_leaderbord_content, contents.sha)  

    # Add new leaderboard results as a comment
    add_comment("## New Leaderboard\n" + df.to_markdown()) 

if __name__ == '__main__':
    add_comment("SageMaker Running...")


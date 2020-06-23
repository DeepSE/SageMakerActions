# Original code from 
# https://github.com/harupy/comment-on-pr/blob/master/entrypoint.py
from github import Github
import os
import json
import pandas as pd
import base64
from io import BytesIO, StringIO
from sagemaker.analytics import TrainingJobAnalytics

def add_comment(message):
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))
    repos_name = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PR_NUMBER')

    if pr_number is None or repos_name is None:
        exit(-1)
    
    pr_number = int(pr_number)

    print("name", repos_name)
    print("number", pr_number)

    repo = gh.get_repo(repos_name)
    pr = repo.get_pull(pr_number)
    
    pr.create_issue_comment(message)

def get_comment_content(key):
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))
    repos_name = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PR_NUMBER')

    if pr_number is None or repos_name is None:
        return None
    
    repo = gh.get_repo(repos_name)
    pr = repo.get_pull(pr_number)

    values = []
    for comment in pr.get_issue_comments():
        if comment.body.startswith(key):
            if len(comment.body)>len(key):
                value = comment.body[len(key):]
                values.append(value)
    
    return values

if __name__ == '__main__':
    add_comment("hi there")
    values = get_comment_content('model_data=')
    for value in values:
        add_comment('found models' + value)





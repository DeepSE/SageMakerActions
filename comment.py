from github import Github
import os
import json
import pandas as pd
import base64
from io import BytesIO, StringIO
from sagemaker.analytics import TrainingJobAnalytics

class Comment:
    repo = None
    pr = None

    def __init__(self, pr_number=None):
        gh = Github(os.getenv('GITHUB_TOKEN'))
        repo_name = os.getenv('GITHUB_REPOSITORY')
        self.repo = gh.get_repo(repo_name)

        # PR_NUMBER: ${{ github.event.number }} # Only available for pr (no push)
        pr_number = pr_number or os.getenv('PR_NUMBER') or "-1"
        pr_number = int(pr_number)

        if pr_number == -1:
            print("No pr number")
            return

        print("PR_NUMBER", pr_number)
        self.pr = self.repo.get_pull(pr_number)

    def add_comment(self, message):
        if self.pr is None:
            return
        
        self.pr.create_issue_comment(message)

    def get_comment(self, key):
        if self.pr is None:
            return None

        values = []
        for comment in self.pr.get_issue_comments():
            if comment.body.startswith(key):
                if len(comment.body)>len(key):
                    value = comment.body[len(key):]
                    values.append(value)
        
        return values
    
    def update_comment(self, key, value):
        if self.pr is None:
            return None

        count = 0
        for comment in self.pr.get_issue_comments():
            if comment.body.startswith(key):
                comment.edit(value)
                count += 1
        
        return count

    def del_comment(self, key):
        if self.pr is None:
            return None

        count = 0
        for comment in self.pr.get_issue_comments():
            if comment.body.startswith(key):
                comment.delete()
                count += 1
        
        return count

if __name__ == '__main__':
    comment = Comment()

    comment.update_comment("hi there", "new hi there")
    comment.add_comment("hi there")
    values = comment.get_comment('model_data=')
    comment.add_comment('\n'.join(values))



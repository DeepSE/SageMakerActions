from github import Github
import os
import json
import pandas as pd
import base64
from io import BytesIO, StringIO
from comment import Comment

class ResultReport():
    def __init__(self):
        self.comment = Comment()

    def report(self, model_data, metrics_df):
        model_data_report = "model_data=" + model_data
        self.comment.add_comment(model_data_report)
        
        result_md = "## Results\n"+ metrics_df.to_markdown()
        self.comment.add_comment(result_md)

    # FIXME: Where to store the leaderboard
    def update_leaderboard(self, score, scoreText="Score", ascending=False, 
        leaderboard_indicator = ".leaderboard.data.donot.remove\n",):
    
        pr_number = self.comment.pr.number 
        pr_sender = self.comment.pr.user.login 

        entry = "#" + str(pr_number) + " by " + str(pr_sender)
    
        leaderboard_content = None

        comment_pr1 = Comment(pr_number=1)
        values = comment_pr1.get_comment(leaderboard_indicator)

        if comment_pr1 is None or len(values) is 0:
                    leaderboard_content = scoreText + ", Entity"
        else:
            leaderboard_content = values[0]

        # Delete the csv comment
        comment_pr1.del_comment(leaderboard_indicator)

        df = pd.read_csv(StringIO(leaderboard_content))
        df.loc[len(df.index)] =  [score, entry] 
        df = df.sort_values(by=df.columns[0], ascending=ascending)
        new_leaderbord_content = df.to_csv(index=False)

        comment_pr1.add_comment(leaderboard_indicator + new_leaderbord_content)

        # Add new leaderboard results as a comment
        leaderboard_md = "## New Leaderboard\n" + df.to_markdown()
        self.comment.add_comment(leaderboard_md)

if __name__ == '__main__':
    pass
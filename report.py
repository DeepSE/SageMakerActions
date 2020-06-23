# Original code from 
# https://github.com/harupy/comment-on-pr/blob/master/entrypoint.py
from github import Github
import os
import json
import pandas as pd
import base64
from io import BytesIO, StringIO
from sagemaker.analytics import TrainingJobAnalytics
from comment import Comment

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


# FIXME: Where to store the leaderboard
def update_leaderboard(score, scoreText="Score", 
        leaderboard_indicator = ".leaderboard.csv\n", 
        lb_branch_name = "_lb_",
        ascending=False):
    
    comment = Comment()

    pr_number = comment.pr.number 
    pr_sender = comment.pr.user.login 

    entry = "#" + str(pr_number) + " by " + str(pr_sender)
 
    leaderboard_content = None

    comment_pr1 = Comment(pr_number=1)
    values = comment_pr1.get_comment(leaderboard_indicator)

    if comment_pr1 is None or len(values) is 0:
                leaderboard_content = scoreText + ", Entity"
    else:
        leaderboard_content = values[0]

    # Delete the comment
    comment_pr1.del_comment(leaderboard_indicator)

    df = pd.read_csv(StringIO(leaderboard_content))
    df.loc[len(df.index)] =  [score, entry] 
    df = df.sort_values(by=df.columns[0], ascending=ascending)
    new_leaderbord_content = df.to_csv(index=False)

    comment_pr1.add_comment(leaderboard_indicator + new_leaderbord_content)

    # Add new leaderboard results as a comment
    leaderboard_md = "## New Leaderboard\n" + df.to_markdown()
    comment.add_comment(leaderboard_md)

def report(lb_config):
    ########################################################################
    # DONOT EDIT AFTER THIS LINE
    ########################################################################
    estimator = lb_config['estimator']
    score_name = lb_config['score_name']
    score_metric = lb_config['score_metric']

    comment = Comment()

    training_job_name = estimator.latest_training_job.name
    trained_model_location = "model_data=" + estimator.model_data
    print(trained_model_location)
    comment.add_comment(trained_model_location)
    
    # Get metric values
    metric_names = [ metric['Name'] for metric in estimator.metric_definitions ] 

    metrics_dataframe = TrainingJobAnalytics(training_job_name=training_job_name, metric_names=metric_names).dataframe()
    result_md = "## Results\n"+ metrics_dataframe.to_markdown()
    print(result_md)
    comment.add_comment(result_md)

    # Update leaderboard. Make sure the key name is right
    # Use any name if you don't want to use the leaderboard
    if score_metric not in metric_names:
        print("leaderboard key name is not correct. No leaderboard support.")
        exit(-1)

    accuracy_df = TrainingJobAnalytics(
        training_job_name=training_job_name, metric_names=[score_metric]).dataframe()

    df_len = len(accuracy_df.index)
    if df_len == 0:
        print("No results to report")
        update_leaderboard(0, scoreText=score_name, ascending=False)
    else:
        value = accuracy_df.loc[df_len-1]['value']
        print("Uploading leaderboard: " + str(value) )
        update_leaderboard(value, scoreText=score_name)


if __name__ == '__main__':
    pass



# Original code from 
# https://github.com/harupy/comment-on-pr/blob/master/entrypoint.py
from github import Github
import os
import json
import pandas as pd
import base64
from io import BytesIO, StringIO
from sagemaker.analytics import TrainingJobAnalytics

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
    # search a pull request that triggered this action
    gh = Github(os.getenv('GITHUB_TOKEN'))
    

    # https://developer.github.com/webhooks/event-payloads/#pull_request
    event = read_json(os.getenv('GITHUB_EVENT_PATH'))
    repo = gh.get_repo(event['repository']['full_name'])
    pr = repo.get_pull(int(event['number']))

    # Testing
    repos_name = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('PR_NUMBER')
    pr.create_issue_comment(repos_name + ":" + pr_number)


    pr_number = pr.number
    pr_sender = event['sender']['login']
    entry = "#" + str(pr_number) + " by " + str(pr_sender)
 
    leaderboard_content = None
    pr1 = repo.get_pull(1)
    for comment in pr1.get_issue_comments():
        if comment.body.startswith(leaderboard_indicator):
            if len(comment.body)>len(leaderboard_indicator):
                leaderboard_content = comment.body[len(leaderboard_indicator):]
            comment.delete()
    
    if not leaderboard_content:
        leaderboard_content = scoreText + ", Entity"
    
    df = pd.read_csv(StringIO(leaderboard_content))
    df.loc[len(df.index)] =  [score, entry] 
    df = df.sort_values(by=df.columns[0], ascending=ascending)
    new_leaderbord_content = df.to_csv(index=False)

    pr1.create_issue_comment(leaderboard_indicator + new_leaderbord_content)

    # Add new leaderboard results as a comment
    leaderboard_md = "## New Leaderboard\n" + df.to_markdown()
    leaderboard_md_base64 = base64.b64encode(leaderboard_md.encode("utf-8")).decode("utf-8")
    print(f"::set-output name=LEADERBOARD_MD::{leaderboard_md_base64}")

def report(lb_config):
    ########################################################################
    # DONOT EDIT AFTER THIS LINE
    ########################################################################
    estimator = lb_config['estimator']
    score_name = lb_config['score_name']
    score_metric = lb_config['score_metric']

    training_job_name = estimator.latest_training_job.name
    trained_model_location = "model_data=" + estimator.model_data
    print(trained_model_location)
    trained_model_location_base64 = base64.b64encode(trained_model_location.encode("utf-8")).decode("utf-8")
    print(f"::set-output name=MODEL_LOCATION::{trained_model_location_base64}")
    
    # Get metric values
    metric_names = [ metric['Name'] for metric in estimator.metric_definitions ] 

    metrics_dataframe = TrainingJobAnalytics(training_job_name=training_job_name, metric_names=metric_names).dataframe()
    result_md = "## Results\n"+ metrics_dataframe.to_markdown()
    print(result_md)

    result_md_base64 = base64.b64encode(result_md.encode("utf-8")).decode("utf-8")
    print(f"::set-output name=RESULT_MD::{result_md_base64}")

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
    result_md = "Testing!"
    print(f"::set-output name=RESULT_MD::{result_md}")

    leaderboard_md = "## New Leaderboard\n"
    print(f"::set-output name=LEADERBOARD_MD::{leaderboard_md}")

    trained_model_location="test.gz"
    print(f"::set-output name=MODEL_LOCATION::{trained_model_location}")



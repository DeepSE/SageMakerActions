import sagemaker
import boto3
from sagemaker.analytics import TrainingJobAnalytics
from sagemaker.pytorch import PyTorch

sagemaker_session = sagemaker.Session(boto3.session.Session())

# Put the right role and input data
role = "arn:aws:iam::294038372338:role/hunkimSagemaker"
inputs = "s3://sagemaker-us-west-2-294038372338/sagemaker/hunkim-pytorch-mnist"

# Make sure the metric_definition and its regex
# Train_epoch=1.0000;  Train_loss=0.8504;
# Test_loss=0.3227;  Test_accuracy=0.9100;
metric_definitions=[
                        {'Name': 'test:loss', 'Regex': 'Test_loss=(.*?);'},
                        {'Name': 'test:accuracy', 'Regex': 'Test_accuracy=(.*?);'},
                        {'Name': 'train:loss', 'Regex': 'Train_loss=(.*?);'},
                        {'Name': 'train:epoch', 'Regex': 'Train_epoch=(.*?);'}
                    ]

estimator = PyTorch(entry_point='mnist.py',
                    source_dir='code',
                    role=role,
                    framework_version='1.4.0',
                    train_instance_count=2,
                    train_instance_type='ml.c4.xlarge',
                    metric_definitions=metric_definitions,
                    hyperparameters={
                        'epochs': 1,
                        'backend': 'gloo'
                    })

estimator.fit({'training': inputs})


########################################################################
# DONOT EDIT AFTER THIS LINE
########################################################################
training_job_name = estimator.latest_training_job.name
desc = sagemaker_session.sagemaker_client.describe_training_job(TrainingJobName=training_job_name)
trained_model_location = desc['ModelArtifacts']['S3ModelArtifacts']
print(trained_model_location)

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(desc)

# Get metric values
metric_names = [ metric['Name'] for metric in metric_definitions ] 

metrics_dataframe = TrainingJobAnalytics(training_job_name=training_job_name, metric_names=metric_names).dataframe()
md = "## Trained Model\n* " + trained_model_location + \
     "\n## Results\n"+ metrics_dataframe.to_markdown()
print(md)

# Add comment
from report_pr_comment import add_comment, update_leaderboard
add_comment(md)

# Update leaderboard. Make sure the key name is right
# Use any name if you don't want to use the leaderboard
accuracy_name = 'test:accuracy'
if accuracy_name not in metric_names:
    print("leaderboard key name is not correct. No leaderboard support.")
    exit(-1)

accuracy_df = TrainingJobAnalytics(
    training_job_name=training_job_name, metric_names=[accuracy_name]).dataframe()

df_len = len(accuracy_df.index)
if df_len == 0:
    print("No results to report")
    update_leaderboard(0, scoreText="Test Accuracy")
else:
    value = accuracy_df.loc[df_len-1]['value']
    print("Uploading leaderboard: " + str(value) )
    update_leaderboard(value, scoreText="Test Accuracy")
import sagemaker
import boto3
from sagemaker.pytorch import PyTorch
from sagemaker.analytics import TrainingJobAnalytics
from report import ResultReport

sagemaker_session = sagemaker.Session(boto3.session.Session())

# Put the right role and input data
role = "arn:aws:iam::445772965351:role/fngo-sagemaker-execution-role"
inputs = "s3://sagemaker-dev-aicel/mnist/"

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
    
# Get metric values
metric_names = [ metric['Name'] for metric in estimator.metric_definitions ] 
metrics_dataframe = TrainingJobAnalytics(training_job_name=training_job_name, metric_names=metric_names).dataframe()

# Report results
rr = ResultReport()
rr.report(estimator.model_data, metrics_dataframe)
    
# Update leaderboard. Make sure the key name is right
# Use any name if you don't want to use the leaderboard
score_metric = 'test:accuracy'
score_name = 'Test Accuracy'
leaderboard_ascending = False

if score_metric not in metric_names:
    print("leaderboard key name is not correct. No leaderboard support.")
    exit(-1)

accuracy_df = TrainingJobAnalytics(
    training_job_name=training_job_name, metric_names=[score_metric]).dataframe()

df_len = len(accuracy_df.index)
if df_len == 0:
    score = 0
else:  # Use the last value as the new score
    score = accuracy_df.loc[df_len-1]['value']

# Update new score to the leaderboard
rr.update_leaderboard(score, scoreText=score_name)

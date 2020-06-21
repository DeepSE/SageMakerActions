import sagemaker
import boto3

sagemaker_session = sagemaker.Session(boto3.session.Session())

from sagemaker.pytorch import PyTorch

# Put the right role and input data
role = "arn:aws:iam::294038372338:role/hunkimSagemaker"
inputs = "s3://sagemaker-us-west-2-294038372338/sagemaker/hunkim-pytorch-mnist"

# Make sure the metric_definition regex
# Train_epoch=1.0000;  Train_loss=0.8504;
# Test_loss=0.3227;  Test_accuracy=0.9100;
estimator = PyTorch(entry_point='mnist.py',
                    source_dir='code',
                    role=role,
                    framework_version='1.4.0',
                    train_instance_count=2,
                    train_instance_type='ml.c4.xlarge',
                    metric_definitions=[
                        {'Name': 'test:loss', 'Regex': 'Test_loss=(.*?);'},
                        {'Name': 'test:accuracy', 'Regex': 'Test_accuracy=(.*?);'},
                        {'Name': 'train:loss', 'Regex': 'Train_loss=(.*?);'},
                        {'Name': 'train:epoch', 'Regex': 'Train_epoch=(.*?);'}
                    ],
                    hyperparameters={
                        'epochs': 1,
                        'backend': 'gloo'
                    })

estimator.fit({'training': inputs})

training_job_name = estimator.latest_training_job.name
desc = sagemaker_session.sagemaker_client.describe_training_job(TrainingJobName=training_job_name)
trained_model_location = desc['ModelArtifacts']['S3ModelArtifacts']
print(trained_model_location)

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(desc)

# Loss: 0.673603
# Test set: Average loss: 0.3227, Accuracy: 9100/10000 (91%)
from sagemaker.analytics import TrainingJobAnalytics

metric_names = ['train:loss', 'test:loss', 'test:accuracy']

metrics_dataframe = TrainingJobAnalytics(training_job_name=training_job_name, metric_names=metric_names).dataframe()
md = "## Trained Model\n* " + trained_model_location + \
    "\n## Results\n"+ metrics_dataframe.to_markdown()
print(md)

from report_pr_comment import add_comment
add_comment(md)
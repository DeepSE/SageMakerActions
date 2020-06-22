import sagemaker
import boto3
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

leaderboard_config = {
    'score_metric': 'test:accuracy', 
    'score_name': 'Test Accuracy',
    'ascending': False,
    'estimator': estimator
    }

# Report results 
# DONOT REMOVE
from report import report
report(leaderboard_config)
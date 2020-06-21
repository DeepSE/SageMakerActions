import sagemaker
import boto3

sagemaker_session = sagemaker.Session(boto3.session.Session())

from sagemaker.pytorch import PyTorch

role = "arn:aws:iam::294038372338:role/hunkimSagemaker"
inputs = "s3://sagemaker-us-west-2-294038372338/sagemaker/hunkim-pytorch-mnist"
estimator = PyTorch(entry_point='mnist.py',
                    source_dir='code',
                    role=role,
                    framework_version='1.4.0',
                    train_instance_count=2,
                    train_instance_type='ml.c4.xlarge',
                    hyperparameters={
                        'epochs': 1,
                        'backend': 'gloo'
                    })

estimator.fit({'training': inputs})


training_job_name = estimator.latest_training_job.name
desc = sagemaker_session.sagemaker_client.describe_training_job(TrainingJobName=training_job_name)
trained_model_location = desc['ModelArtifacts']['S3ModelArtifacts']
print(trained_model_location)
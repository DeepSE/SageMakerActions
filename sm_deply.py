import sagemaker
import boto3
from sagemaker.pytorch import PyTorch
from sagemaker.pytorch import PyTorchModel

sagemaker_session = sagemaker.Session(boto3.session.Session())

# Put the right role and input data
role = "arn:aws:iam::294038372338:role/hunkimSagemaker"

model = PyTorchModel(model_data=model_data,
                     role=role,
                     framework_version='1.5.0',
                     entry_point='que_gen.py',
                     source_dir='code',
                     predictor_cls=JSONPredictor)

predictor = model.deploy(initial_instance_count=1, instance_type='ml.m4.xlarge')

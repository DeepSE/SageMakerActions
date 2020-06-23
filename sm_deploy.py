import sagemaker
import boto3
from sagemaker.pytorch import PyTorch
from sagemaker.pytorch import PyTorchModel
from comment import Comment

sagemaker_session = sagemaker.Session(boto3.session.Session())

# Put the right role and input data
role = "arn:aws:iam::294038372338:role/hunkimSagemaker"

comment = Comment()
values = comment.get_comment('model_data=')
if values is None or len(values) == 0:
    comment.add_comment('Deploy Fail: no model data. Did you train?')
    exit(-1)

print("Data:", values[-1])

model = PyTorchModel(model_data=values[-1],
                     role=role,
                     framework_version='1.5.0',
                     entry_point='mnist.py',
                     source_dir='code')


comment.add_comment('Deploying with data ' + values[-1])
try:
    predictor = model.deploy(initial_instance_count=1, instance_type='ml.m4.xlarge')
    comment.add_comment('end_point=' + predictor.endpoint)
except Exception as e:
    comment.add_comment('Deploy Fail:' + str(e))

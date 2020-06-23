import sagemaker
import boto3
from sagemaker.pytorch import PyTorch
from sagemaker.pytorch import PyTorchModel
from comment import Comment

sagemaker_session = sagemaker.Session(boto3.session.Session())

# Put the right role and input data
role = "arn:aws:iam::294038372338:role/hunkimSagemaker"

comment = Comment()
values = comment.get_comment('end_point=')
if values is None or len(values) == 0:
    comment.add_comment('Delete Fail: no endpoint to delete. Did you deploy?')
    exit(-1)

print("Endpoint:", values[-1])

model = PyTorchModel(model_data=values[-1],
                     role=role,
                     framework_version='1.5.0',
                     entry_point='mnist.py',
                     source_dir='code')


comment.add_comment('Deleting endpoint ' + values[-1])
try:
    sagemaker_session.delete_endpoint(values[-1])
    comment.add_comment('Endpoint ' + values[-1] + ' deleted!')
    comment.del_comment('end_point=')
except Exception as e:
    comment.add_comment('Deleting endpoint Fail:' + str(e))

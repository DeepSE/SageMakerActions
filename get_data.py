from torchvision import datasets, transforms
import sagemaker

sagemaker_session = sagemaker.Session()

bucket = sagemaker_session.default_bucket()
prefix = 'sagemaker/hunkim-pytorch-mnist'

role = "arn:aws:iam::294038372338:role/hunkimSagemaker"

datasets.MNIST('data', download=True, transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
]))

inputs = sagemaker_session.upload_data(path='data', bucket=bucket, key_prefix=prefix)
print('input spec (in this case, just an S3 path): {}'.format(inputs))

with open("s3_input_url.txt", 'w') as f:
    f.write(inputs)
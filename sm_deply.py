
from sagemaker.pytorch import PyTorchModel

model = PyTorchModel(model_data=model_data,
                     role=role,
                     framework_version='1.5.0',
                     entry_point='que_gen.py',
                     source_dir='code',
                     predictor_cls=JSONPredictor)

predictor = model.deploy(initial_instance_count=1, instance_type='ml.m4.xlarge')

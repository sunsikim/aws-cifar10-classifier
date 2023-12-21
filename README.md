# aws-cifar10-classifier

Basically, this repository re-implements CNN image classifier training logic over CIFAR10 dataset implemented in [this repository](https://github.com/sunsikim/demo-cifar10-classifier/tree/master). However, unlike previous attempt where model is trained on local Apple M2 silicon machine, this repository implements same logic to be executed on remote AWS GPU instance. Specifically, this repository includes following steps:

1. [Create IAM user and setup appropriate IAM permission](#1-create-authorized-iam-user)
2. [Let the user launch instance using Deep Learning AMI](#2-launch-deep-learning-instance)
3. [Run Deep Learning Container within the instance](#3-run-deep-learning-container)
4. [Train model and upload SavedModel to S3](#4-train-model-within-the-container)
5. [Validate model using streamlit demo](#5-deploy-streamlit-demo-within-instance)
6. [Clean-up created resources](#6-resource-clean-up)

## 1. Create authorized IAM user

Assuming that we created administrator user, configured its profile into AWS CLI and got `boto3`, `typer` installed in the virtual environment using following commands, we are good to go.

```shell
aws configure  # configure administrator profile
python3 -V     # Python 3.10.10
python3 -m venv venv
source venv/bin/activate
pip install boto3 typer
```

## 2. Launch Deep Learning Instance



## 3. Run Deep Learning Container



## 4. Train model within the container



## 5. streamlit demo deployment


## 6. Resource clean-up
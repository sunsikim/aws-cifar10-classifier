# aws-cifar10-classifier

Basically, this repository re-implements CNN image classifier training logic over CIFAR10 dataset implemented in [this repository](https://github.com/sunsikim/demo-cifar10-classifier/tree/master). However, unlike previous attempt where model is trained on local Apple M2 silicon machine, this repository implements same logic to be executed on remote AWS GPU instance. Specifically, this repository includes following steps:

1. [Launch instance using Deep Learning AMI](#1-launch-deep-learning-instance)
1. [Run Deep Learning Container within the instance](#2-run-deep-learning-container)
1. [Train model and upload SavedModel to S3](#3-train-model-within-the-container)
1. [Validate model using streamlit demo](#4-streamlit-demo-deployment)
1. [Clean-up created resources](#5-resource-clean-up)

Assuming that we created administrator user, configured its profile into AWS CLI and got `boto3`, `typer` installed in the virtual environment using following commands, we are good to go.

```shell
aws configure  # configure administrator profile
python3 -V     # Python 3.10.10
python3 -m venv venv
source venv/bin/activate
pip install boto3 typer
```

## 1. Launch Deep Learning Instance

Commands in `commands` directory are mostly copied and pasted from [existing repository](https://github.com/sunsikim/aws-ec2-workspace-setup), so check there for related details. One difference is AMI ID fetching part, since application would require special drivers to be installed to run implemented logic successfully. As a result, instance has to be launched on specific Deep Learning AMI, so its AMI ID has to be fetched accordingly like below. 

```python

```

Other minor changes are:

* Since streamlit demo has to be launched in the instance, public access on port 8501 is opened. Ports for jupyter applications are all closed. 
* As private subnet is unnecessary, corresponding case handling part is removed from the method.

## 2. Run Deep Learning Container



## 3. Train model within the container



## 4. Streamlit demo deployment


## 5. Resource clean-up
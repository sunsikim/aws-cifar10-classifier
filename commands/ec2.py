import pathlib
import time

from commands.vpc import fetch_vpc_security_group_id, fetch_subnet_id

INSTANCE_NAME = "cifar10"
KEY_NAME = "workspace"


def get_ami_id(ec2_client):
    response = ec2_client.describe_images(
        Owners=["amazon"],
        IncludeDeprecated=False,
        IncludeDisabled=False,
        DryRun=False,
        Filters=[
            {
                "Name": "name",
                "Values": ["Deep Learning AMI GPU TensorFlow 2.11.? (Ubuntu 20.04) ????????"]
            },
            {
                "Name": "state",
                "Values": ["available"]
            }
        ]
    )["Images"]
    ami = sorted(response, key=lambda x: x["CreationDate"], reverse=True)[0]
    return ami["ImageId"]


def create_key_pair(ec2_client, local_dir: pathlib.Path):
    """
    Create key pair to access remote EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :param local_dir: path to directory to save key pair file
    :return: None
    """
    key_info = ec2_client.create_key_pair(
        KeyName=KEY_NAME,
        DryRun=False,
        KeyType="rsa",
        KeyFormat="pem",
    )
    key_path = local_dir.joinpath(f"{KEY_NAME}.pem")
    with open(key_path, "w") as file:
        file.write(key_info["KeyMaterial"])
    key_path.chmod(0o400)  # python equivalent to 'chmod 400 key_path'


def run_instance(ec2_client):
    """
    Launch instance and wait until it gets ready
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    response = ec2_client.run_instances(
        ImageId=get_ami_id(ec2_client),
        InstanceType="g3.4xlarge",
        KeyName=KEY_NAME,
        SecurityGroupIds=[fetch_vpc_security_group_id(ec2_client)],
        SubnetId=fetch_subnet_id(ec2_client),
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": INSTANCE_NAME}]
            }
        ]
    )
    instance_id = response["Instances"][0]["InstanceId"]
    is_running = False
    while not is_running:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_running = instance_info["State"]["Name"] == "running"


def stop_instance(ec2_client):
    """
    Stop EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.stop_instances(InstanceIds=[instance_id])
    is_stopped = False
    while not is_stopped:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_stopped = instance_info["State"]["Name"] == "stopped"


def start_instance(ec2_client):
    """
    Start stopped EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.start_instances(InstanceIds=[instance_id])
    is_running = False
    while not is_running:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_running = instance_info["State"]["Name"] == "running"


def reboot_instance(ec2_client):
    """
    Reboot EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.reboot_instances(InstanceIds=[instance_info["InstanceId"]])
    is_running = False
    while not is_running:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_running = instance_info["State"]["Name"] == "running"


def terminate_instance(ec2_client):
    """
    Associate elastic IP with EC2 instance
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    instance_info = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
            {"Name": "subnet-id", "Values": [fetch_subnet_id(ec2_client)]}
        ]
    )["Reservations"][0]["Instances"][0]
    instance_id = instance_info["InstanceId"]
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    is_terminated = False
    while not is_terminated:
        time.sleep(3)
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance_info = response["Reservations"][0]["Instances"][0]
        is_terminated = instance_info["State"]["Name"] == "terminated"


def describe_instance(ec2_client):
    """
    Print current status of the created instance
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "subnet-id",
                    "Values": [fetch_subnet_id(ec2_client)]
                },
                {
                    "Name": "tag:Name",
                    "Values": [INSTANCE_NAME]
                }
            ]
        )
        instance_info = response["Reservations"][0]["Instances"][0]
        state = instance_info["State"]["Name"]
        print(f"CURRENT STATE  : {state}")
        if state == "running":
            print(f'LAUNCH COMMAND : ssh -i "{KEY_NAME}.pem" ubuntu@{instance_info["PublicDnsName"]}')
    except Exception:
        print("Instance has not been created yet")


def delete_key_pair(ec2_client, local_dir: pathlib.Path):
    """
    Delete created key pair
    :param ec2_client: EC2 client created by boto3 session
    :param local_dir: path to directory where key pair file was saved
    :return: None
    """
    pathlib.os.remove(local_dir.joinpath(f"{KEY_NAME}.pem"))
    ec2_client.delete_key_pair(KeyName=KEY_NAME)

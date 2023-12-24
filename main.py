import boto3
import pathlib
import commands.ec2 as ec2_commands
import commands.vpc as vpc_commands
import typer

app = typer.Typer()


@app.command("vpc")
def manage_vpc(
        action_type: str = typer.Argument(...),
        profile_name: str = typer.Argument(...),
        region_name: str = typer.Argument("ap-northeast-2"),
):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client("ec2")
    if action_type.lower() == "create":
        vpc_commands.create_vpc(ec2_client)
        vpc_commands.create_vpc_security_group(ec2_client)
        vpc_commands.create_vpc_internet_gateway(ec2_client)
    elif action_type.lower() == "delete":
        vpc_commands.delete_vpc_security_group(ec2_client)
        vpc_commands.delete_vpc_internet_gateway(ec2_client)
        vpc_commands.delete_vpc(ec2_client)
    else:
        raise ValueError(f"action_type must be one of ('create', 'delete'); got: '{action_type}'")


@app.command("subnet")
def manage_subnet(
        action_type: str = typer.Argument(...),
        profile_name: str = typer.Argument(...),
        region_name: str = typer.Argument("ap-northeast-2"),
):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client("ec2")
    if action_type.lower() == "create":
        vpc_commands.create_subnet(ec2_client, region_name)
        vpc_commands.create_route_table(ec2_client)
        vpc_commands.create_route_table_subnet_association(ec2_client)
    elif action_type.lower() == "delete":
        vpc_commands.delete_route_table_subnet_association(ec2_client)
        vpc_commands.delete_route_table(ec2_client)
        vpc_commands.delete_subnet(ec2_client)
    else:
        raise ValueError(f"action_type must be one of ('create', 'delete'); got: '{action_type}'")


@app.command("instance")
def manage_instance(
        action_type: str = typer.Argument(...),
        profile_name: str = typer.Argument(...),
        region_name: str = typer.Argument("ap-northeast-2"),
):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client("ec2")
    if action_type.lower() == "run":
        ec2_commands.run_instance(ec2_client)
    elif action_type.lower() == "start":
        ec2_commands.start_instance(ec2_client)
    elif action_type.lower() == "stop":
        ec2_commands.stop_instance(ec2_client)
    elif action_type.lower() == "reboot":
        ec2_commands.reboot_instance(ec2_client)
    elif action_type.lower() == "terminate":
        ec2_commands.terminate_instance(ec2_client)
    elif action_type.lower() == "describe":
        ec2_commands.describe_instance(ec2_client)
    else:
        raise ValueError(
            f"action_type must be one of ('run', 'start', 'stop', 'reboot', 'terminate', 'describe'); got: '{action_type}'"
        )


@app.command("key-pair")
def manage_key_pair(
        action_type: str = typer.Argument(...),
        profile_name: str = typer.Argument(...),
        region_name: str = typer.Argument("ap-northeast-2"),
        key_dir: str = typer.Argument("."),
):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client("ec2")
    local_dir = pathlib.Path(key_dir).resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    if action_type.lower() == "create":
        ec2_commands.create_key_pair(ec2_client, local_dir)
    elif action_type.lower() == "delete":
        ec2_commands.delete_key_pair(ec2_client, local_dir)
    else:
        raise ValueError(f"action_type must be one of ('create', 'delete'); got: '{action_type}'")


if __name__ == "__main__":
    app()

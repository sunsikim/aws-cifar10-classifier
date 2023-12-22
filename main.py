import boto3
import pathlib
import commands.ec2 as ec2_commands
import commands.vpc as vpc_commands
import typer
from typing import Optional

app = typer.Typer()


@app.command("vpc")
def manage_vpc(
        action_type: str = typer.Argument(...),
        profile_name: str = typer.Argument(...),
        region_name: str = typer.Argument(...),
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
        region_name: str = typer.Argument(...),
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
        profile_name: str = typer.Option(...),
        region_name: str = typer.Option(...),
        vpc_name: str = typer.Option(...),
        subnet_name: str = typer.Option(...),
        instance_name: str = typer.Option(...),
        image_id: Optional[str] = typer.Option(None),
        instance_type: Optional[str] = typer.Option(None),
        key_name: Optional[str] = typer.Option(None),
):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client("ec2")
    if action_type.lower() == "run":
        ec2_commands.run_instance(
            ec2_client=ec2_client,
            image_id=image_id,
            instance_type=instance_type,
            key_name=key_name,
            subnet_name=subnet_name,
            instance_name=instance_name,
        )
    elif action_type.lower() == "start":
        ec2_commands.start_instance(
            ec2_client=ec2_client,
            subnet_name=subnet_name,
            instance_name=instance_name,
        )
    elif action_type.lower() == "stop":
        ec2_commands.stop_instance(
            ec2_client=ec2_client,
            subnet_name=subnet_name,
            instance_name=instance_name,
        )
    elif action_type.lower() == "reboot":
        ec2_commands.reboot_instance(
            ec2_client=ec2_client,
            subnet_name=subnet_name,
            instance_name=instance_name,
        )
    elif action_type.lower() == "terminate":
        ec2_commands.terminate_instance(
            ec2_client=ec2_client,
            subnet_name=subnet_name,
            instance_name=instance_name,
        )
    elif action_type.lower() == "describe":
        ec2_commands.describe_instance(
            ec2_client=ec2_client,
            subnet_name=subnet_name,
            instance_name=instance_name,
        )

    else:
        raise ValueError(
            f"action_type must be one of ('run', 'start', 'stop', 'reboot', 'terminate', 'describe'); got: '{action_type}'"
        )


@app.command("key-pair")
def manage_key_pair(
        action_type: str = typer.Argument(...),
        profile_name: str = typer.Option(...),
        region_name: str = typer.Option(...),
        key_name: str = typer.Option(...),
        key_dir: Optional[str] = typer.Option("."),
):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client("ec2")
    local_dir = pathlib.Path(key_dir).resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    if action_type.lower() == "create":
        ec2_commands.create_key_pair(
            ec2_client=ec2_client,
            key_name=key_name,
            local_dir=local_dir,
        )
    elif action_type.lower() == "delete":
        ec2_commands.delete_key_pair(
            ec2_client=ec2_client,
            key_name=key_name,
            local_dir=local_dir,
        )
    else:
        raise ValueError(f"action_type must be one of ('create', 'delete'); got: '{action_type}'")


if __name__ == "__main__":
    app()

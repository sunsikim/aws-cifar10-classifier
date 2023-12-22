from typing import List

VPC_NAME = "workspace"
VPC_CIDR = "172.50.0.0/16"  # subnet mask = 255.255.0.0
INGRESS_PORTS = ["22", "80", "5000-5005", "8501"]
SUBNET_NAME = "public"
ROUTE_TABLE_NAME = "rt-pub"


def create_vpc(ec2_client):
    """
    Create VPC whose value for name tag is VPC_NAME and covers IP range defined as vpc_cidr(subnet mask: 255.255.0.0).
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    response = ec2_client.create_vpc(
        CidrBlock=VPC_CIDR,
        TagSpecifications=[
            {
                "ResourceType": "vpc",
                "Tags": [{"Key": "Name", "Value": VPC_NAME}]
            }
        ]
    )
    vpc_id = response["Vpc"]["VpcId"]
    ec2_client.modify_vpc_attribute(
        EnableDnsHostnames={"Value": True},
        VpcId=vpc_id
    )


def create_vpc_security_group(ec2_client):
    """
    Create default security group within VPC and authorize connections to ingress ports
    :param ec2_client: EC2 client created by boto3 session
    :return: ID of security group
    """
    vpc_id = fetch_vpc_id(ec2_client)
    response = ec2_client.create_security_group(
        GroupName=f"{VPC_NAME}-sg",
        Description="traffic rules over EC2 workspace",
        VpcId=vpc_id,
    )
    sg_id = response["GroupId"]
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=_parse_ip_permissions(INGRESS_PORTS)
    )


def create_vpc_internet_gateway(ec2_client):
    """
    Create internet gateway and attach it to a VPC
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    igw_id = ec2_client.create_internet_gateway(
        TagSpecifications=[
            {
                "ResourceType": "internet-gateway",
                "Tags": [{"Key": "Name", "Value": f"{VPC_NAME}-igw"}]
            }
        ]
    )["InternetGateway"]["InternetGatewayId"]
    vpc_id = fetch_vpc_id(ec2_client)
    ec2_client.attach_internet_gateway(
        InternetGatewayId=igw_id, VpcId=vpc_id
    )


def create_subnet(ec2_client, region_name: str):
    """
    Create a subnet within a VPC. Subnet attribute 'MapPubilcIpOnLaunch' is modified to True to assign public IPv4
    address to instance created within the subnet.
    :param ec2_client: EC2 client created by boto3 session
    :param region_name: name of region
    :return: None
    """
    vpc_id = fetch_vpc_id(ec2_client)
    vpc_info = ec2_client.describe_vpcs(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )["Vpcs"][0]
    subnet_cidr = vpc_info["CidrBlock"].split(".")[:-1]  # ex. '172.50.0.0/16' -> ['172', '50', '0']
    subnet_cidr[2] = "100"  # ex. ['172', '50', '0'] -> ['172', '50', '100']
    subnet_cidr = f"{'.'.join(subnet_cidr)}.0/24"  # ex. ['172', '50', '100'] -> '172.50.100.0/24'
    response = ec2_client.create_subnet(
        CidrBlock=subnet_cidr,
        VpcId=vpc_id,
        AvailabilityZone=f"{region_name}a",
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [{"Key": "Name", "Value": SUBNET_NAME}]
            }
        ]
    )
    subnet_id = response["Subnet"]["SubnetId"]
    ec2_client.modify_subnet_attribute(
        SubnetId=subnet_id,
        MapPublicIpOnLaunch={"Value": True},
    )


def create_route_table(ec2_client):
    """
    Create basic route table that allows traffic from VPC. If `is_public` is set to True, add route to internet gateway
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    vpc_id = fetch_vpc_id(ec2_client)
    response = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                "ResourceType": "route-table",
                "Tags": [{"Key": "Name", "Value": ROUTE_TABLE_NAME}]
            }
        ]
    )
    igw_info = ec2_client.describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
    )["InternetGateways"]
    assert len(igw_info) > 0, f"Internet gateway attached to VPC '{VPC_NAME}' is not generated"
    ec2_client.create_route(
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=igw_info[0]["InternetGatewayId"],
        RouteTableId=response["RouteTable"]["RouteTableId"],
    )


def create_route_table_subnet_association(ec2_client):
    """
    Associate created route table to created subnet
    :param ec2_client: EC2 client created by boto3 session
    :return:
    """
    subnet_id = fetch_subnet_id(ec2_client)
    rt_id = ec2_client.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [fetch_vpc_id(ec2_client)]},
            {"Name": "tag:Name", "Values": [ROUTE_TABLE_NAME]}
        ]
    )["RouteTables"][0]["RouteTableId"]
    ec2_client.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)


def fetch_vpc_id(ec2_client) -> str:
    """
    This project assigns unique name to unique VPC, so normal response should contain only one set of VPC information.
    If list is empty, it means that VPC is not created. If there are multiple VPCs with given name, it must be that
    one of VPCs is created from outside of this project.
    :param ec2_client: EC2 client created by boto3 session
    :return: VpcId
    """
    vpc_info = ec2_client.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [VPC_NAME]}]
    )["Vpcs"]
    if len(vpc_info) == 1:
        return vpc_info[0]["VpcId"]
    elif len(vpc_info) == 0:
        raise ValueError(f"VPC with name '{VPC_NAME}' does not exists")
    else:
        raise ValueError(f"VPC whose name tag value is '{VPC_NAME}' is ambiguous")


def fetch_vpc_security_group_id(ec2_client) -> str:
    """
    One-to-one correspondence between security group and sg_name is checked as explained in `fetch_vpc_id` method.
    :param ec2_client: EC2 client created by boto3 session
    :return: GroupId
    """
    sg_name = f"{VPC_NAME}-sg"
    sg_info = ec2_client.describe_security_groups(
        Filters=[
            {"Name": "vpc-id", "Values": [fetch_vpc_id(ec2_client)]},
            {"Name": "group-name", "Values": [sg_name]},
        ]
    )["SecurityGroups"]
    if len(sg_info) == 1:
        return sg_info[0]["GroupId"]
    elif len(sg_info) == 0:
        raise ValueError(f"Security group with GroupName '{sg_name}' does not exists")
    else:
        raise ValueError(f"Security group with GroupName '{sg_name}' is ambiguous")


def fetch_subnet_id(ec2_client) -> str:
    """
    One-to-one correspondence between subnet and SUBNET_NAME is checked as explained in `fetch_vpc_id` method.
    :param ec2_client: EC2 client created by boto3 session
    :return: SubnetId
    """
    subnet_info = ec2_client.describe_subnets(
        Filters=[
            {"Name": "vpc-id", "Values": [fetch_vpc_id(ec2_client)]},
            {"Name": "tag:Name", "Values": [SUBNET_NAME]}
        ]
    )["Subnets"]
    if len(subnet_info) == 1:
        return subnet_info[0]["SubnetId"]
    elif len(subnet_info) == 0:
        raise ValueError(f"Subnet with name '{SUBNET_NAME}' does not exists")
    else:
        raise ValueError(f"Subnet whose name tag value is '{SUBNET_NAME}' is ambiguous")


def delete_route_table_subnet_association(ec2_client):
    """
    Delete association between route table and subnet
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    vpc_id = fetch_vpc_id(ec2_client)
    associated_subnet_id = fetch_subnet_id(ec2_client)
    rt_info = ec2_client.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "association.subnet-id", "Values": [associated_subnet_id]},
            {"Name": "tag:Name", "Values": [ROUTE_TABLE_NAME]},
        ]
    )["RouteTables"][0]
    ec2_client.disassociate_route_table(
        AssociationId=rt_info["Associations"][0]["RouteTableAssociationId"]
    )


def delete_route_table(ec2_client):
    """
    Delete route table from VPC
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    vpc_id = fetch_vpc_id(ec2_client)
    rt_info = ec2_client.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [ROUTE_TABLE_NAME]},
        ]
    )["RouteTables"][0]
    ec2_client.delete_route_table(RouteTableId=rt_info["RouteTableId"])


def delete_subnet(ec2_client):
    """
    Delete subnet from VPC
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    subnet_id = fetch_subnet_id(ec2_client)
    ec2_client.delete_subnet(SubnetId=subnet_id)


def delete_vpc_security_group(ec2_client):
    """
    Delete default security group of VPC
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    security_group_id = fetch_vpc_security_group_id(ec2_client)
    ec2_client.delete_security_group(GroupId=security_group_id)


def delete_vpc_internet_gateway(ec2_client):
    """
    Detach internet gateway of given VPC and delete it consecutively
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    vpc_id = fetch_vpc_id(ec2_client)
    igw_info = ec2_client.describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
    )["InternetGateways"]
    igw_id = igw_info[0]["InternetGatewayId"]
    ec2_client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)


def delete_vpc(ec2_client):
    """
    Delete VPC whose tagged name is VPC_NAME
    :param ec2_client: EC2 client created by boto3 session
    :return: None
    """
    vpc_id = fetch_vpc_id(ec2_client)
    ec2_client.delete_vpc(VpcId=vpc_id)


def _parse_ip_permissions(ingress_ports: List[str]):
    """
    Parse ingress port and convert it into port ingress permission statement. If ingress port string is:
        * single integer, both FromPort and ToPort
        * string that contains hyphen between two integers,
        * otherwise, return error since the value is not in expected format
    :param ingress_ports: list of port(ex. '22') or range of ports(ex. '8888-8890')
    :return: list of parsed permissions
    """
    permission_statements = []
    for ingress_port in ingress_ports:
        try:
            from_port = int(ingress_port)
            to_port = int(ingress_port)
        except ValueError:  # ValueError with message 'invalid literal for int() with base 10'
            if "-" in ingress_port:
                from_port, to_port = map(int, ingress_port.split("-"))
            else:
                raise ValueError(
                    f"ingress_port should be either integer or contains '-' as separator; got {ingress_port}"
                )
        if from_port == to_port:
            description = f"allow any connection attempt on port {from_port}"
        else:
            description = f"allow any connection attempt on port {from_port} to {to_port} (inclusive)"
        parsed_permission = {
            "FromPort": from_port,
            "ToPort": to_port,
            "IpProtocol": "tcp",
            "IpRanges": [
                {
                    "CidrIp": "0.0.0.0/0",
                    "Description": description
                }
            ]
        }
        permission_statements.append(parsed_permission)
    return permission_statements

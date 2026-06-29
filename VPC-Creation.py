import boto3

client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

print("Let's start building a VPC...")

tag = input("Give a name for your tag: ")
vpc_pool = input("Your VPC Network: ")
sub_net = input("Your Subnet Network: ")

print(f"Creating VPC with tag {tag}...")

############# Create VPC ################

vpc_response = client.create_vpc(
    CidrBlock=vpc_pool,
    TagSpecifications=[
        {
            'ResourceType': 'vpc',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tag
                }
            ]
        }
    ]
)

vpc_id = vpc_response['Vpc']['VpcId']

print(f"VPC ID: {vpc_id}")

print(f"{tag} VPC has been created.")

############# Create Internet Gateway ################

print(f"Creating Internet Gateway for {tag}...")

igw_response = client.create_internet_gateway(
    TagSpecifications=[
        {
            'ResourceType': 'internet-gateway',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tag
                }
            ]
        }
    ]
)

igw_id = igw_response['InternetGateway']['InternetGatewayId']

print(f"Internet Gateway ID: {igw_id}")

############# Attach Internet Gateway ################

print(f"Attaching Internet Gateway to {tag} VPC...")

client.attach_internet_gateway(
    InternetGatewayId=igw_id,
    VpcId=vpc_id
)

print("Internet Gateway attached successfully.")

############# Create Route Table ################

print("Creating Route Table...")

route_table_response = client.create_route_table(
    VpcId=vpc_id,
    TagSpecifications=[
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tag
                }
            ]
        }
    ]
)

route_table_id = route_table_response['RouteTable']['RouteTableId']

print(f"Route Table ID: {route_table_id}")

############# Create Route ################

client.create_route(
    RouteTableId=route_table_id,
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=igw_id
)

print("Default route created.")

############# Create Subnet ################

print("Creating Subnet...")

subnet_response = client.create_subnet(
    VpcId=vpc_id,
    CidrBlock=sub_net,
    TagSpecifications=[
        {
            'ResourceType': 'subnet',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tag
                }
            ]
        }
    ]
)

subnet_id = subnet_response['Subnet']['SubnetId']

print(f"Subnet ID: {subnet_id}")
print(tag, "Subnet created...")

############# Associate Route Table ################

client.associate_route_table(
    RouteTableId=route_table_id,
    SubnetId=subnet_id
)

print("Route Table associated with Subnet", tag, ".")

############ Create Security Group #####################
print("Creating Security group...")
security_group = client.create_security_group(
    GroupName=tag, Description=f"{tag} Security Group", VpcId=vpc_id)
client.authorize_security_group_ingress(
    GroupId=security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'icmp',
            'FromPort': -1,
            'ToPort': -1,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        }
    ]
)
client.authorize_security_group_ingress(
    GroupId=security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        }
    ]
)
client.authorize_security_group_ingress(
    GroupId=security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        }
    ]
)
client.authorize_security_group_ingress(
    GroupId=security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        }
    ]
)
print(security_group)
print("Security Group Created...")

############## Create ec2 Instance##############
instance = ec2.create_instances(
    ImageId='ami-09aa82e803f05d496',
    InstanceType='t3.micro',
    MaxCount=1, MinCount=1,
    NetworkInterfaces=[
        {
            'SubnetId': subnet_id, 
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [security_group['GroupId']]
        }
    ],
    TagSpecifications=[
        {
            'ResourceType': 'ec2',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tag
                }
            ]
        }
    ]
)

instance[0].wait_until_running()

print(instance[0].id)
print("ec2 instance created")

print(f"\nInfrastructure '{tag}' created successfully!")


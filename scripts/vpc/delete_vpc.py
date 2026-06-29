import boto3

client = boto3.client('ec2')

############# Get all VPCs ###################
vpc_response = client.describe_vpcs()

############# Get all Internet Gateways ###################
igw_response = client.describe_internet_gateways()

############# Detach and Delete Internet Gateways ###################
for igw in igw_response['InternetGateways']:

    if igw['Attachments']:

        vpc_id = igw['Attachments'][0]['VpcId']
        igw_id = igw['InternetGatewayId']

        vpc = client.describe_vpcs(VpcIds=[vpc_id])

        if not vpc['Vpcs'][0]['IsDefault']:

            client.detach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id
            )

            client.delete_internet_gateway(
                InternetGatewayId=igw_id
            )

            print(f"Deleted Internet Gateway: {igw_id}")

############# Delete Non-Default VPCs ###################
for vpc in vpc_response['Vpcs']:

    if not vpc.get('IsDefault', False):

        client.delete_vpc(
            VpcId=vpc['VpcId']
        )

        print(f"Deleted VPC: {vpc['VpcId']}")
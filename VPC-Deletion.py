import boto3

client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

user_tag = input("Please provide the user tag: ").strip()
print("========== EC2 Instance Manager ==========\n")

# Get all instances
response = client.describe_instances()
sec_response = client.describe_security_groups()
rt_response = client.describe_route_tables()
ig_response = client.describe_internet_gateways()
sub_response = client.describe_subnets()

instances = {}

routetables={}

count = 0
print("Available EC2 Instances")
print("-------------------------------------------------------------")

for reservation in response['Reservations']:

    for instance in reservation['Instances']:

        instance_id = instance['InstanceId']
        state = instance['State']['Name']

        name = "No Name Tag"

        for tag in instance.get('Tags', []):

            if tag['Key'] == 'Name':
                name = tag['Value']
                break

        instances[instance_id] = name

        print(f"Name : {name}")
        print(f"ID   : {instance_id}")
        print(f"State: {state}")
        print("-------------------------------------------------------------")
        count = count+1

print(f'We have {count} number of Instances...')

if count == 0:
    print("You have no instances in your account...")
    print("Skipping Ec2 cleanup process...")
else:    
    # Ask the user which instance to terminate
    instance_id = input("\nEnter the Instance ID to terminate: ").strip()

    # Validate the instance exists
    if instance_id not in instances:
        print("Invalid Instance ID.")
        exit()

    print(f"\nSelected Instance : {instances[instance_id]}")

    reply = input("Do you want to terminate this EC2 instance? (yes/no): ").strip().lower()

    if reply != "yes":
        print("Operation cancelled.")
        exit()

    print("\n⚠ WARNING: This action will permanently terminate the EC2 instance.")

    confirm = input(
        f"Type DELETE to permanently terminate '{instances[instance_id]}': "
    ).strip()

    if confirm != "DELETE":
        print("Confirmation failed. EC2 instance was NOT terminated.")
        exit()

    print("\nTerminating instance...")

    client.terminate_instances(
        InstanceIds=[instance_id]
    )

    ec2.Instance(instance_id).wait_until_terminated()

    print(f"\nEC2 instance '{instances[instance_id]}' has been terminated successfully.")

########## Deleting the security Group ####################
print("-------------------------------------------------------------")
print("Available Security Groups")
print("-------------------------------------------------------------")

for sec_grp in sec_response['SecurityGroups']:

    group_id = sec_grp['GroupId']
    vpc_id = sec_grp['VpcId']
    ip_perm_id=sec_grp['IpPermissions']
    grp_name=sec_grp['GroupName']
    
    print(f"Name : {grp_name}")
    print(f"ID   : {group_id}")
    print(f"VPC ID: {vpc_id}")
    print("-------------------------------------------------------------")

# Ask the user which instance to terminate
del_sec_id = input("Give me the ID of the Security Group you want to delete:")
if del_sec_id == "default":
    print("You cannot delete the default security group.")
    exit()
elif del_sec_id == "":
    print("No Security Group ID provided. Moving to next step...")
else:    
    print("Initiating Security Group deletion sequence...")
    client.delete_security_group(GroupId=del_sec_id)
    print("Security Group Deleted...")

print("-------------------------------------------------------------")
print("Available Route Tables")
print("-------------------------------------------------------------")

for rt_tbl in rt_response['RouteTables']:

    rt_id = rt_tbl['RouteTableId']
    vpc_id = rt_tbl['VpcId']

    rt_name = "No Name Tag"

    # Get the Name tag of the Route Table
    for tag in rt_tbl.get('Tags', []):

        if tag['Key'] == 'Name':
            rt_name = tag['Value']
            break

    routetables[rt_id] = rt_name

    print(f"Name    : {rt_name}")
    print(f"ID      : {rt_id}")
    print(f"VPC ID  : {vpc_id}")
    print("=====================================================================")
    # Print association information
    for association in rt_tbl.get('Associations', []):

        association_id = association.get('RouteTableAssociationId', "N/A")
        state = association.get('AssociationState', {}).get('State', "Unknown")
        main = association.get('Main', False)
        
        print(f"Association ID : {association_id}")
        print(f"State          : {state}")
        print(f"Main           : {main}")

print("-------------------------------------------------------------")
art_del_input=input("Please provide the Association ID you want to delete (or press Enter to skip):   ")
if art_del_input == "":
    print("No Association ID provided. Moving to next step...")
else:
    client.disassociate_route_table(AssociationId=art_del_input)
    print("Route Table Dissociated...")

rt_del_input=input("Please provide the Route Table ID you want to delete (or press Enter to skip):   ")
if rt_del_input == "":
    print("No Route Table ID provided. Moving to next step...")
else:
    print("Deleting the Route Table...")
    client.delete_route_table(RouteTableId=rt_del_input)
    print("Route Table Deleted")
    print("-------------------------------------------------------------")
##################### Detaching Internet Gateway ########################
print("-------------------------------------------------------------")
print("Available Internet Gateways")
print("-------------------------------------------------------------")

for igw in ig_response['InternetGateways']:

    igw_id = igw['InternetGatewayId']
    igw_name = "No Name Tag"      # Reset for every Internet Gateway

    # Find the Name tag
    for tg in igw.get('Tags', []):
        if tg['Key'] == 'Name':
            if tg['Value'] == user_tag:
                igw_name = tg['Value']
            break

    # Print attachment details
    for attachment in igw.get('Attachments', []):

        vpc_id = attachment.get('VpcId', "N/A")
        state = attachment.get('State', "Unknown")

        print(f"Name   : {igw_name}")
        print(f"ID     : {igw_id}")
        print(f"VPC ID : {vpc_id}")
        print(f"State  : {state}")
        print("-------------------------------------------------------------")

ig_input=input("Please provide the Internet Gateway ID you want to detach (or press Enter to skip):")
vpc_id = input("Please provide the VPC ID associated with the Internet Gateway (or press Enter to skip):")
if ig_input == "":
    print("No Internet Gateway ID provided. Moving to next step...")
else:
    # Detach the Internet Gateway
    print("Detaching the Internet Gateway...")
    client.detach_internet_gateway(InternetGatewayId=ig_input, VpcId=vpc_id)
    print("Internet Gateway Detached...")

    print("-------------------------------------------------------------")
    print("Deleteing the Internet Gateway...")
    # Delete the Internet Gateway
    print("Deleting the Internet Gateway...")
    client.delete_internet_gateway(InternetGatewayId=ig_input)
    print("Internet Gateway Deleted...")

################ Delete the Subnet ########################
print("-------------------------------------------------------------")
print("Available Subnets")
print("-------------------------------------------------------------")

for sub in sub_response['Subnets']:

    sub_id = sub['SubnetId']
    vpc_id = sub['VpcId']
    sub_name = "No Name Tag"      # Reset for every Subnet

    # Find the Name tag
    for tg in sub.get('Tags', []):
        if tg['Key'] == 'Name':
            if tg['Value'] == user_tag:
                sub_name = tg['Value']
            break

    print(f"Name   : {sub_name}")
    print(f"ID     : {sub_id}")
    print(f"VPC ID : {vpc_id}")
    print("-------------------------------------------------------------")

sub_input=input("Please provide the Subnet ID you want to delete (or press Enter to skip):")
if sub_input == "":
    print("No Subnet ID provided. Moving to next step...")
else:
    # Delete the Subnet
    print("Deleting the Subnet...")
    client.delete_subnet(SubnetId=sub_input)
    print("Subnet Deleted...")
print("------------------------------------------------------------------")

##################### Delete the VPC ########################
print("-------------------------------------------------------------")
print("Available VPCs")
print("-------------------------------------------------------------")

for vpc in client.describe_vpcs()['Vpcs']:

    vpc_id = vpc['VpcId']
    vpc_name = "No Name Tag"

    # Find the Name tag
    for tg in vpc.get('Tags', []):
        if tg['Key'] == 'Name':
            vpc_name = tg['Value']
            break

    # Check whether this VPC belongs to the project
    if vpc_name == user_tag:
        match = " <-- MATCH"
    else:
        match = ""

    print(f"Name : {vpc_name}{match}")
    print(f"ID   : {vpc_id}")
    print("-------------------------------------------------------------")

vpc_input = input("Please provide the VPC ID you want to delete (or press Enter to skip): ").strip()

if vpc_input == "":
    print("No VPC ID provided. Exiting the script...")
else:
    print("Deleting the VPC...")
    client.delete_vpc(VpcId=vpc_input)
    print("VPC Deleted...")
    print("-------------------------------------------------------------")


print("\n Congratulations!, All basic resources in our VPC have been deleted successfully.")

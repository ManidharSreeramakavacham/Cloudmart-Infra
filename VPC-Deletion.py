import boto3

client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

print("========== EC2 Instance Manager ==========\n")

# Get all instances
response = client.describe_instances()
sec_response = client.describe_security_groups()

instances = {}

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
del_sec_id = input("Give me the ID of the Security Group tou want to delete:")
print("Initiating Security Group deletion sequence...")
client.delete_security_group(GroupId=del_sec_id)
print("Security Group Deleted...")
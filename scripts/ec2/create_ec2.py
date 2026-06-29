import boto3
import time

from config import (
    AWS_REGION,
    AMI_ID,
    INSTANCE_TYPE,
    KEY_PAIR_NAME,
    INSTANCE_NAME
)

from utils.state_manager import save_state

ec2 = boto3.resource(
    "ec2",
    region_name=AWS_REGION
)

print("Creating EC2 instance...")
print(f"AMI_ID: {repr(AMI_ID)}")
print(f"INSTANCE_TYPE: {repr(INSTANCE_TYPE)}")
print(f"KEY_PAIR_NAME: {repr(KEY_PAIR_NAME)}")
print(f"INSTANCE_NAME: {repr(INSTANCE_NAME)}")

instances = ec2.create_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    KeyName=KEY_PAIR_NAME,
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {
            "ResourceType":"instance",
            "Tags":[
                {
                    "Key": "Name",
                    "Value": INSTANCE_NAME
                }
            ]
        }
    ]
)

instance = instances[0]

print(f"Instance Id: {instance.id}")

print("Waiting for instance to enter running state...")

instance.wait_until_running()

instance.reload()

print("\nEC2 instance created successfully!")
print("------------------------------------------")
print(f"Instance ID: {instance.id}")

state = {
    "instance_id": instance.id,
    "instance_name": INSTANCE_NAME,
    "region": AWS_REGION,
    "public_ip": instance.public_ip_address
}

save_state(state)

print("Instance ID saved to instance_id.txt")    
print(f"Public IP Address: {instance.public_ip_address}")
print(f"State: {instance.state['Name']}")
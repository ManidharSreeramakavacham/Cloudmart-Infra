import boto3

from config import AWS_REGION

from utils.state_manager import load_state

state = load_state()

instance_id = state["instance_id"]

ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION
)

print(f"Stopping Instance: {instance_id}...")

ec2.stop_instances(
    InstanceIds=[instance_id]
)

waiter = ec2.get_waiter("instance_stopped")

print("Waiting for instance to stop...")

waiter.wait(
    InstanceIds=[instance_id]   
)

print("Instance stopped successfully!")
import boto3
import os

from config import AWS_REGION
from pathlib import Path
from utils.state_manager import load_state

state = load_state()

instance_id = state["instance_id"]

ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION
)

print(f"Terminating Instance: {instance_id}...")

ec2.terminate_instances(
    InstanceIds = [instance_id]
)

waiter = ec2.get_waiter("instance_terminated")

print("Waiting for instance to terminate...")

waiter.wait(
    InstanceIds=[instance_id]  
)

print("Instance terminated successfully!")

Path("state.json").unlink(missing_ok=True)

print(f"state.json file removed successfully.")
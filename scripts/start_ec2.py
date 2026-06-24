import boto3

from config import AWS_REGION

from utils.state_manager import load_state, save_state

state = load_state()

INSTANCE_ID = state["instance_id"]

ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION
)

print(f"Starting Instance: {INSTANCE_ID}")

ec2.start_instances(
    InstanceIds=[INSTANCE_ID]
)

waiter = ec2.get_waiter("instance_running")

print("Waiting for instance to start...")

waiter.wait(
    InstanceIds=[INSTANCE_ID]
)

response = ec2.describe_instances(
    InstanceIds=[INSTANCE_ID]
)

instance = response["Reservations"][0]["Instances"][0]

state["public_ip"] = instance["PublicIpAddress"]

save_state(state)

print("\nInstance Started Successfully")
print("-----------------------------")
print(f"Instance ID : {INSTANCE_ID}")
print(f"Public IP   : {instance.get('PublicIpAddress')}")
print(f"State       : {instance['State']['Name']}")


import boto3

ec2 = boto3.client("ec2")

regions = ec2.describe_regions()

for region in regions["Regions"]:
    print(region["RegionName"])
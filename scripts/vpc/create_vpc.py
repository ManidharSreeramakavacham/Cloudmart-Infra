import boto3
import json

############# Create a VPC #######################
ec2 = boto3.resource('ec2', region_name='ap-south-2')
client = boto3.client('ec2')

vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "Test"}])
vpc.wait_until_available()
print(vpc.id)
print("VPC Created with the name tag {vpc.tags[0]['Value']}")
############## Create an internet Gateway #############

ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId = ig.id)
print(ig.id)
print("Internet Gateway Created and Attached with VPC.")
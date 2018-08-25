'''
author: Tresor Omari
Date 8/23/18
V.02

'''
'''
This script will provision an Infrastructure with a website accessible through https. 

we will use the EC2's public dns name as domain name
1. Define the default session
2. Create Security Group
3. Create Subnets (us-west-2a and us-west-2b)
4. Generate and save the keypair
5. Launch two instances (in different subnets)
6. Create ELB and register the instances
'''

#================================================================================================= 

import boto3
import time #I will use this module to pause the script


# first, I need to define the default session. since I want this script to work for anyone, you will...
# ...have to enter your own access key, secret key, and region in which you work

aKey = str(input('Enter your Access Key: ')) 
sKey = str(input('Enter your Secret Key: '))
region = 'us-west-2'                    
print()

# 1. Define the default session
boto3.setup_default_session(aws_access_key_id= aKey, aws_secret_access_key=sKey, region_name=region)

ec2 = boto3.resource('ec2')

# 2. create a security group

# The security group will have the port 80, 443, and 22 open. 
import boto3

# Create Security Group

secGroup = ec2.create_security_group(GroupName='WebServer', Description='port 443,80, and 22 are open')
secGroup.create_tags(Tags=[{"Key":"Name", "Value": "WebServer"}])
secGroup.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort = 443,
    ToPort = 443
)
secGroup.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort = 80,
    ToPort = 80
)
secGroup.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort = 22,
    ToPort = 22
)
secGroupId = secGroup.id
print('Security Group..............Done!') # I will use the same security group for all instances and ELB

# 3. Create Subnets ##############################################################################
################################################################################################
cidr01=input(str('Please Enter the CIDR for subnet 1 (us-west-2a): ')) 
cidr02=input(str('Please Enter the CIDR for subnet 2 (us-west-2b): ')) 
vpcId= input(str('Please Enter your Default VPCId: ')) 

# Subnet 1 - this is the first subnet. by default I placed this to us-west-2a.
subnet001 = ec2.create_subnet(CidrBlock=cidr01,AvailabilityZone='us-west-2a',VpcId=vpcId) 
subnet001.create_tags(Tags=[{"Key":"Name", "Value": "SubNet001 Demo"}])
subNetId01=subnet001.id
print('Subnet 001......Done!')

# Subnet 2 - this is the second subnet. by default I placed this to us-west-2b
subnet002 = ec2.create_subnet(CidrBlock=cidr02,AvailabilityZone='us-west-2b', VpcId=vpcId) 
subnet002.create_tags(Tags=[{"Key":"Name", "Value": "SubNet002 Demo"}])
subNetId02=subnet002.id
print('Subnet 002......Done!')

# 4. Generate new SSH Key Pair

import boto3

client = boto3.client('ec2')
keypair = client.create_key_pair(KeyName='TheKey')

time.sleep(3)


# This code below is used to save the pem file to your Windows system (C:\users\)
# This is the reason why you need to run this script as admin
#open a file
k=open("C:\\Users\\TheKey.pem","w+")  
print(keypair['KeyMaterial'],file=k) 
time.sleep(2)
print('Keypair..............Done!')
# The file is saved at this point
####################

# 5. Launch two instances 

import boto3
client01 = boto3.resource('ec2')

# I created the user data shebang for the first EC2 instance. the only difference with the other user data is...
#...that I install ansible in this one.
usrDataAnsController='''#!/bin/bash
yum update -y
amazon-linux-extras install ansible2 -y
amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
yum install -y httpd mariadb-server
systemctl start httpd
yum install mod_ssl -y
systemctl restart httpd
systemctl enable httpd
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;
echo "<h1>Hey Guys, This is the https version!!!</h1>" > /var/www/html/index.html
'''
# This is the second user data shebang 
usrData='''#!/bin/bash
yum update -y
amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
yum install -y httpd mariadb-server
systemctl start httpd
yum install mod_ssl -y
systemctl restart httpd
systemctl enable httpd
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;
echo "<h1>Hey Guys, This is the https version!!!</h1>" > /var/www/html/index.html
'''
# Both instances will use the same keypair (TheKey)
# Create the first instance with ansible installed.

instance01 = client01.create_instances(ImageId='ami-6cd6f714', KeyName='TheKey', InstanceType='t2.micro',UserData=usrDataAnsController, MaxCount=1,MinCount=1, NetworkInterfaces=[
                                  {'SubnetId': subNetId01 ,'DeviceIndex': 0,'AssociatePublicIpAddress': True, 'Groups': [secGroup.group_id]}])

# Create the second instance
instance02 = client01.create_instances(ImageId='ami-6cd6f714', KeyName='TheKey', InstanceType='t2.micro',UserData=usrData, MaxCount=1,MinCount=1, NetworkInterfaces=[
                                  {'SubnetId': subNetId02 ,'DeviceIndex': 0,'AssociatePublicIpAddress': True, 'Groups': [secGroup.group_id]}])
# I paused to give time to the instances to be in running state

print('This will take forever!!!')
time.sleep(2)
print('I am just kidding :)')
time.sleep(3)
print('According to AWS, it takes 60 sec for an EC2 instance to be in running state.')
time.sleep(4)
print('I could have used get_waiter function, but it was not working and my time was limited!!!')
time.sleep(4)
print('we almost there....')
time.sleep(7)
print()
# put some time sleep here later
print('Instances......Done')


# 5. Create ELB 
# I will not use the ELB, only created this to show you that the website will be available dynamically in 2 differents A-Z
import boto3

elb= boto3.client('elb')

loadBal = elb.create_load_balancer(
    LoadBalancerName='CaseWareELBDemo',
    Listeners=[
        {
            'Protocol':'HTTP',
            'LoadBalancerPort':80,
            'InstanceProtocol':'HTTP',
            'InstancePort':80
        },
    ],
    AvailabilityZones=['us-west-2a','us-west-2b'],
    SecurityGroups=[secGroup.group_id]
)

health_check=elb.configure_health_check(
    LoadBalancerName='CaseWareELBDemo',
    HealthCheck={
        'Target':'TCP:22',
        'Interval':10,
        'Timeout':5,
        'UnhealthyThreshold':5,
        'HealthyThreshold':5

    }
)

print('ELB.......Done!')

# You will need to copy the instance Id and paste them here if you want to register them to the ELB

# Instance 01 - us-west-2a
I_id01=input(str('Please enter the first Instance Id : '))

# Instance 02 - us-west-2b
I_id02=input(str('Please enter the second Instance Id : '))

# Attach Instances

import boto3
attachinst = elb.register_instances_with_load_balancer(
    LoadBalancerName='CaseWareELBDemo',
    Instances=[
        {
            'InstanceId':I_id01
        },
        {
            'InstanceId':I_id02
        }
    ]
)
print()
print("IT IS FINISHED!!!!")
#=================================================================================================
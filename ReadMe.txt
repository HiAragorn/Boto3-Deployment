Read Me - Instructions.
======================
Below is what I used to create this script, and I highly recommend you to use the same environment.

!!! Make sure to run the script as admin. the reason why you should do it is because it will save the keypair file to your c drive. !!!

Prerequisites
==============
OS: Windows 10
IDE: Microsoft Visual Code
Python Version: Python 3.5.0

=========
Region : us-west-2
A-Z: us-west-2a and us-west-2b
=========

Even though the script is doing the job for us, you will have to enter some information.

1. Access Key
2. Secret Key
3. I chose the us-west-2 as region for this session. Please stick to it. 
4. CIDR for your subnets
5. the default VPC id
6. When the instances and the ELB will be created, you will be prompted to enter the instances id so they can be attached to the ELB. 

When you receive the message that "IT IS FINISHED"

open your aws console, copy the instance public dns name.
open a browser, type https://instance public dns name

you will get a warning because it is a self signed certificate. 

================
 

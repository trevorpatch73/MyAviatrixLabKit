# Configure AWS provider source
provider "aws" {
  region = "us-east-2"
  access_key = var.aws_key_id
  secret_key = var.aws_key_value
}

# Create Security Groups For Ping Boxes
resource "aws_security_group" "AA_AWS_US_E2_SS" {
  name        = "Any-Any"
  description = "Allow All Traffic"
  vpc_id      = aviatrix_vpc.AWS-US-E2-SHR-SVCS-VPC.id

  ingress {
    description      = "Any-Any"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Project = "Aviatrix"
  }
}

#Create interfaces to reach our ping boxes
resource "aws_network_interface" "SHR_SVCS_SRV_01_IFACE_01" {
  subnet_id   = aviatrix_vpc.AWS-US-E2-SHR-SVCS-VPC.public_subnets[0].cidr
  security_groups = [aws_security_group.AA_AWS_US_E2_SS.id]

  tags = {
    Name = "primary_network_interface"
    Project = "Aviatrix"
  }
}

# Create the Ping Boxes
resource "aws_instance" "SHR_SVCS_SRV_01" {
    ami           = "ami-064ff912f78e3e561"
    instance_type = "t2.micro"
    key_name      = "AWS-US-E2_KeyPair"
    network_interface {
        network_interface_id = aws_network_interface.SHR_SVCS_SRV_01_IFACE_01.id
        device_index         = 0
    }
    availability_zone = "us-east-2a"
    user_data = <<EOF
        #!/bin/bash -ex
         yum -y install epel-release
         yum -y install iperf
         sudo iperf -s [-p 5001]
        EOF
    tags = {
        Project = "Aviatrix"
    }
}

# Create & Attach EIPs for PingBoxes
resource "aws_eip" "SHR_SVCS_SRV_01_EIP" {
  instance = aws_instance.SHR_SVCS_SRV_01.id
  vpc      = true
}

resource "aws_eip_association" "SHR_SVCS_SRV_01_eip_assoc" {
  instance_id   = aws_instance.SHR_SVCS_SRV_01.id
  allocation_id = aws_eip.SHR_SVCS_SRV_01_EIP.id
}
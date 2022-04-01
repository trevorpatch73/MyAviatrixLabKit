# Configure AWS provider source
provider "aws" {
  region = "us-west-2"
  access_key = var.aws_key_id
  secret_key = var.aws_key_value
}


# Create Security Groups For Ping Boxes
resource "aws_security_group" "AA_AWS_US_W2_BU1_Mono" {
  name        = "Any-Any"
  description = "Allow All Traffic"
  vpc_id      = var.vpc_id

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
resource "aws_network_interface" "BU1_MONO_SRV_01_IFACE_01" {
  subnet_id   = var.subnet_id
  security_groups = [aws_security_group.AA_AWS_US_W2_BU1_Mono.id]

  tags = {
    Name = "primary_network_interface"
    Project = "Aviatrix"
  }
}

# Create the Ping Boxes
resource "aws_instance" "BU1_MONO_SRV_01" {
    ami           = "ami-00ee4df451840fa9d"
    instance_type = "t2.micro"
    key_name      = "AWS-US-W2_KeyPair"
    network_interface {
        network_interface_id = aws_network_interface.BU1_MONO_SRV_01_IFACE_01.id
        device_index         = 0
    }
    availability_zone = "us-west-2a"
    user_data = <<EOF
        #!/bin/bash -ex
         yum -y install epel-release
         yum -y install iperf
         iperf ${var.SHR_SVCS_SRV_01_PRIVATE_IP} --parallel 100 -i 1 -t 2
        EOF
    tags = {
        Project = "Aviatrix"
    }
}

# Create & Attach EIPs for PingBoxes
resource "aws_eip" "BU1_MONO_SRV_01_EIP" {
  instance = aws_instance.BU1_MONO_SRV_01.id
  vpc      = true
}

resource "aws_eip_association" "BU1_MONO_SRV_01_eip_assoc" {
  instance_id   = aws_instance.BU1_MONO_SRV_01.id
  allocation_id = aws_eip.BU1_MONO_SRV_01_EIP.id
}
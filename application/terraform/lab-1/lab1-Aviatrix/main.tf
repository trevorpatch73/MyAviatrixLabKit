# Configure Aviatrix provider source and version
terraform {
  required_providers {
    aviatrix = {
      source = "AviatrixSystems/aviatrix"
      version = "2.21.2"
    }
  }
}

# Configure Aviatrix provider
provider "aviatrix" {
  controller_ip           = var.controller_ip
  username                = "admin"
  password                = "P@ssw0rd"
  skip_version_validation = true
}

# Onboard AWS Account
resource "aviatrix_account" "aws_account" {
  account_name       = var.aws_acct_num
  cloud_type         = 1
  aws_iam            = false
  aws_account_number = var.aws_acct_num
  aws_access_key     = var.aws_key_id
  aws_secret_key     = var.aws_key_value
}

# Create US-East-2 Transit VPC
resource "aviatrix_vpc" "AWS-US-E2-TRNST-VPC" {
  cloud_type           = 1
  account_name         = var.aws_acct_num
  region               = "us-east-2"
  name                 = "AWS-US-E2-TRNST-VPC"
  cidr                 = "30.1.0.0/20"
  aviatrix_transit_vpc = true
  aviatrix_firenet_vpc = false
  depends_on           = [
      aviatrix_account.aws_account,
  ]
}

# Create US-East-2 Shared Services VPC
resource "aviatrix_vpc" "AWS-US-E2-SHR-SVCS-VPC" {
  cloud_type           = 1
  account_name         = var.aws_acct_num
  region               = "us-east-2"
  name                 = "AWS-US-E2-SHR-SVCS-VPC"
  cidr                 = "30.0.1.0/24"
  aviatrix_transit_vpc = false
  aviatrix_firenet_vpc = false
  depends_on           = [
      aviatrix_account.aws_account,
  ]
}

# Create US-WEST-2 BU1 VPC
resource "aviatrix_vpc" "AWS-US-W2-BU1-MONO-VPC" {
  cloud_type           = 1
  account_name         = var.aws_acct_num
  region               = "us-west-2"
  name                 = "AWS-US-W2-BU1-MONO-VPC"
  cidr                 = "30.0.2.0/24"
  aviatrix_transit_vpc = false
  aviatrix_firenet_vpc = false
  depends_on           = [
      aviatrix_account.aws_account,
  ]
}

# Create an Aviatrix AWS Transit Network Gateway
resource "aviatrix_transit_gateway" "AWS-US-E2-TRNST-GW" {
  cloud_type               = 1
  account_name             = var.aws_acct_num
  gw_name                  = "AWS-US-E2-TRNST-GW"
  vpc_id                   = aviatrix_vpc.AWS-US-E2-TRNST-VPC.vpc_id
  vpc_reg                  = "us-east-2"
  gw_size                  = "t2.micro"
  subnet                   = aviatrix_vpc.AWS-US-E2-TRNST-VPC.public_subnets[0].cidr
  tags                     = {
    name = "aviatrix"
  }
  enable_hybrid_connection = false
  connected_transit        = true
  #enable_active_mesh	   = false
}

# Create an Aviatrix AWS SS Spoke Gateway
resource "aviatrix_spoke_gateway" "AWS-US-E2-SHR-SVCS-SPOKE-GW" {
  cloud_type                        = 1
  account_name                      = var.aws_acct_num
  gw_name                           = "AWS-US-E2-SHR-SVCS-SPOKE-GW"
  vpc_id                            = aviatrix_vpc.AWS-US-E2-SHR-SVCS-VPC.vpc_id
  vpc_reg                           = "us-east-2"
  gw_size                           = "t2.micro"
  subnet                            = aviatrix_vpc.AWS-US-E2-SHR-SVCS-VPC.public_subnets[0].cidr
  single_ip_snat                    = false
  manage_transit_gateway_attachment = false
  allocate_new_eip                  = true
  #enable_active_mesh	            = false
  tags                              = {
    name = "aviatrix"
  }
}

# Create an Aviatrix AWS BU1 Spoke Gateway
resource "aviatrix_spoke_gateway" "AWS-US-W2-BU1-MONO-SPOKE-GW" {
  cloud_type                        = 1
  account_name                      = var.aws_acct_num
  gw_name                           = "AWS-US-W2-BU1-MONO-SPOKE-GW"
  vpc_id                            = aviatrix_vpc.AWS-US-W2-BU1-MONO-VPC.vpc_id
  vpc_reg                           = "us-west-2"
  gw_size                           = "t2.micro"
  subnet                            = aviatrix_vpc.AWS-US-W2-BU1-MONO-VPC.public_subnets[0].cidr
  single_ip_snat                    = false
  manage_transit_gateway_attachment = false
  allocate_new_eip                  = true
  #enable_active_mesh	            = false
  tags                              = {
    name = "aviatrix"
  }
}

# Create an Aviatrix Spoke Transit Attachment
resource "aviatrix_spoke_transit_attachment" "SS-SPOKE_TRNST_ATTACHMENT" {
  spoke_gw_name   = aviatrix_spoke_gateway.AWS-US-E2-SHR-SVCS-SPOKE-GW.gw_name
  transit_gw_name = aviatrix_transit_gateway.AWS-US-E2-TRNST-GW.gw_name
}
resource "aviatrix_spoke_transit_attachment" "BU1-SPOKE_TRNST_ATTACHMENT" {
  spoke_gw_name   = aviatrix_spoke_gateway.AWS-US-W2-BU1-MONO-SPOKE-GW.gw_name
  transit_gw_name = aviatrix_transit_gateway.AWS-US-E2-TRNST-GW.gw_name
}

# Create Security Groups For Ping Boxes
resource "aws_security_group" "AA_AWS_US_W2_BU1_Mono" {
  name        = "Any-Any"
  description = "Allow All Traffic"
  vpc_id      = aviatrix_vpc.AWS-US-W2-BU1-MONO-VPC.id

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
  subnet_id   = aviatrix_vpc.AWS-US-W2-BU1-MONO-VPC.public_subnets[0].cidr
  security_groups = [aws_security_group.AA_AWS_US_W2_BU1_Mono.id]

  tags = {
    Name = "primary_network_interface"
    Project = "Aviatrix"
  }
}

# Create the Ping Boxes
resource "aws_instance" "SHR_SVCS_SRV_01" {
  depends_on  = [
    aviatrix_spoke_transit_attachment.SS-SPOKE_TRNST_ATTACHMENT,
    aviatrix_spoke_transit_attachment.BU1-SPOKE_TRNST_ATTACHMENT,
  ]
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

resource "aws_instance" "BU1_MONO_SRV_01" {
  depends_on  = [
    aviatrix_spoke_transit_attachment.SS-SPOKE_TRNST_ATTACHMENT,
    aviatrix_spoke_transit_attachment.BU1-SPOKE_TRNST_ATTACHMENT,
  ]
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
         iperf -c 172.31.1.152 --parallel 100 -i 1 -t 2
        EOF
    tags = {
        Project = "Aviatrix"
    }
}

# Create & Attach EIPs for PingBoxes
resource "aws_eip" "SHR_SVCS_SRV_01_EIP" {
  depends_on  = [
    aviatrix_spoke_transit_attachment.SS-SPOKE_TRNST_ATTACHMENT,
    aviatrix_spoke_transit_attachment.BU1-SPOKE_TRNST_ATTACHMENT,
  ]
  instance = aws_instance.SHR_SVCS_SRV_01.id
  vpc      = true
}

resource "aws_eip" "BU1_MONO_SRV_01_EIP" {
  depends_on  = [
    aviatrix_spoke_transit_attachment.SS-SPOKE_TRNST_ATTACHMENT,
    aviatrix_spoke_transit_attachment.BU1-SPOKE_TRNST_ATTACHMENT,
  ]
  instance = aws_instance.SHR_SVCS_SRV_01.id
  vpc      = true
}

resource "aws_eip_association" "SHR_SVCS_SRV_01_eip_assoc" {
  depends_on  = [
    aviatrix_spoke_transit_attachment.SS-SPOKE_TRNST_ATTACHMENT,
    aviatrix_spoke_transit_attachment.BU1-SPOKE_TRNST_ATTACHMENT,
  ]
  instance_id   = aws_instance.SHR_SVCS_SRV_01.id
  allocation_id = aws_eip.SHR_SVCS_SRV_01_EIP.id
}

resource "aws_eip_association" "BU1_MONO_SRV_01_eip_assoc" {
  depends_on  = [
    aviatrix_spoke_transit_attachment.SS-SPOKE_TRNST_ATTACHMENT,
    aviatrix_spoke_transit_attachment.BU1-SPOKE_TRNST_ATTACHMENT,
  ]
  instance_id   = aws_instance.BU1_MONO_SRV_01.id
  allocation_id = aws_eip.BU1_MONO_SRV_01_EIP.id
}
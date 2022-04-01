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

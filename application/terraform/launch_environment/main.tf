provider "aws" {
  region     = "us-east-1"
  access_key = var.aws_key_id
  secret_key = var.aws_key_value
}

resource "aws_vpc" "aviatrix_vpc" {
    cidr_block = "30.0.0.0/24"

    tags = {
        Project = "Aviatrix"
    }
}

resource "aws_subnet" "aviatrix_subnet" {
    vpc_id = aws_vpc.aviatrix_vpc.id
    cidr_block = "30.0.0.0/24"
    map_public_ip_on_launch = true
    availability_zone = "us-east-1a"

    tags = {
        Project = "Aviatrix"
    }
}

resource "aws_internet_gateway" "aviatrix_igw" {
  vpc_id = aws_vpc.aviatrix_vpc.id

  tags = {
    Project = "Aviatrix"
  }
}

resource "aws_route_table" "aviatrix_rt" {
  vpc_id = aws_vpc.aviatrix_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.aviatrix_igw.id
  }

  tags = {
    Project = "Aviatrix"
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.aviatrix_subnet.id
  route_table_id = aws_route_table.aviatrix_rt.id
}

resource "aws_security_group" "AviatrixSG" {
  name        = "AviatrixSG"
  description = "Allow traffic for SST"
  vpc_id      = aws_vpc.aviatrix_vpc.id
}

resource "aws_security_group_rule" "sst_ingress" {
  type              = "ingress"
  description       = "Allows HTTPS ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.AviatrixSG.id
}

resource "aws_security_group_rule" "sst_egress_https" {
  type              = "egress"
  description       = "Allows HTTPS egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.AviatrixSG.id
}

resource "aws_security_group_rule" "sst_egress_http" {
  type              = "egress"
  description       = "Allows HTTP egress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.AviatrixSG.id
}

resource "aws_network_interface" "aviatrix_iface" {
  subnet_id   = aws_subnet.aviatrix_subnet.id
  security_groups = [aws_security_group.AviatrixSG.id]

  tags = {
    Name = "primary_network_interface"
    Project = "Aviatrix"
  }
}

resource "aws_instance" "sst" {
    ami                    = "ami-0ba0368134698fdd8"
    instance_type          = "t3.micro"
    ebs_optimized          = false
    monitoring             = false
    network_interface {
        network_interface_id = aws_network_interface.aviatrix_iface.id
        device_index         = 0
    }

    root_block_device {
        volume_type = "gp2"
        volume_size = 8
    }

    availability_zone = "us-east-1a"

    tags = {
        Name = "Aviatrix Self Starter Tool"
        Project = "Aviatrix"
    }
}
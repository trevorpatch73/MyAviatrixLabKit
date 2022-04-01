output AWS-US-E2-SHR-SVCS-VPC-ID {
  value = aviatrix_vpc.AWS-US-E2-SHR-SVCS-VPC.vpc_id
}
output AWS-US-E2-SHR-SVCS-SUBNET-ID {
  value = aviatrix_vpc.AWS-US-E2-SHR-SVCS-VPC.public_subnets[0].subnet_id
}
output AWS-US-W2-BU1-MONO-VPC-ID {
  value = aviatrix_vpc.AWS-US-W2-BU1-MONO-VPC.vpc_id
}
output AWS-US-W2-BU1-MONO-SUBNET-ID {
  value = aviatrix_vpc.AWS-US-W2-BU1-MONO-VPC.public_subnets[0].subnet_id
}

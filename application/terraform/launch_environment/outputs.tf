output instance_public_ip {
  value = aws_instance.sst.public_ip
}
output instance_private_ip {
  value = aws_instance.sst.private_ip
}
output vpc_id{
    value = aws_vpc.aviatrix_vpc.id
}
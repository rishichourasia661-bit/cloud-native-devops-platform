output "staging_vpc_id" {
  description = "ID of the staging VPC"
  value       = aws_vpc.staging.id
}

output "staging_public_subnet_ids" {
  description = "IDs of the public subnets"
  value = [
    aws_subnet.staging_public_a.id,
    aws_subnet.staging_public_b.id
  ]
}

output "staging_private_subnet_ids" {
  description = "IDs of the private subnets"
  value = [
    aws_subnet.staging_private_a.id,
    aws_subnet.staging_private_b.id
  ]
}
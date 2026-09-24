terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
}

resource "aws_vpc" "staging" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "cloud-native-devops-staging-vpc"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}
resource "aws_subnet" "staging_public_a" {
  vpc_id                  = aws_vpc.staging.id
  cidr_block              = "10.10.1.0/24"
  availability_zone       = "ca-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "cloud-native-devops-staging-public-a"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}

resource "aws_subnet" "staging_public_b" {
  vpc_id                  = aws_vpc.staging.id
  cidr_block              = "10.10.2.0/24"
  availability_zone       = "ca-central-1b"
  map_public_ip_on_launch = true

  tags = {
    Name        = "cloud-native-devops-staging-public-b"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}
resource "aws_internet_gateway" "staging" {
  vpc_id = aws_vpc.staging.id

  tags = {
    Name        = "cloud-native-devops-staging-igw"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}
resource "aws_route_table" "staging_public" {
  vpc_id = aws_vpc.staging.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.staging.id
  }

  tags = {
    Name        = "cloud-native-devops-staging-public-rt"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}
resource "aws_route_table_association" "staging_public_a" {
  subnet_id      = aws_subnet.staging_public_a.id
  route_table_id = aws_route_table.staging_public.id
}

resource "aws_route_table_association" "staging_public_b" {
  subnet_id      = aws_subnet.staging_public_b.id
  route_table_id = aws_route_table.staging_public.id
}
resource "aws_subnet" "staging_private_a" {
  vpc_id            = aws_vpc.staging.id
  cidr_block        = "10.10.11.0/24"
  availability_zone = "ca-central-1a"

  tags = {
    Name        = "cloud-native-devops-staging-private-a"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}

resource "aws_subnet" "staging_private_b" {
  vpc_id            = aws_vpc.staging.id
  cidr_block        = "10.10.12.0/24"
  availability_zone = "ca-central-1b"

  tags = {
    Name        = "cloud-native-devops-staging-private-b"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}
resource "aws_route_table" "staging_private" {
  vpc_id = aws_vpc.staging.id

  tags = {
    Name        = "cloud-native-devops-staging-private-rt"
    Environment = "staging"
    Project     = "cloud-native-devops-platform"
  }
}
resource "aws_route_table_association" "staging_private_a" {
  subnet_id      = aws_subnet.staging_private_a.id
  route_table_id = aws_route_table.staging_private.id
}

resource "aws_route_table_association" "staging_private_b" {
  subnet_id      = aws_subnet.staging_private_b.id
  route_table_id = aws_route_table.staging_private.id
}
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.30"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "eu-central-1"
}

locals {
  default_availability_zone = "eu-central-1a"

  domain_name     = "lexibot.link" // TODO: Extract to parameter.
  www_domain_name = format("www.%s", local.domain_name)
}

variable "DBUSERNAME" {
  description = "The username for the DB master user"
  type        = string
}

variable "DBPASSWORD" {
  description = "The password for the DB master user"
  type        = string
}

resource "aws_instance" "lexibot-instance-main" {
  ami                         = "ami-0767046d1677be5a0"
  availability_zone           = local.default_availability_zone
  ebs_optimized               = false
  instance_type               = "t2.micro"
  monitoring                  = false
  key_name                    = "amazon-lexibot-main"
  vpc_security_group_ids      = ["sg-0a19556524f383a26"]
  associate_public_ip_address = true
  source_dest_check           = true

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 8
    delete_on_termination = true
  }

  tags = {
    Name = "lexibot-main"
  }
}

resource "aws_db_instance" "lexibot-db" {
  identifier              = "lexibot-db"
  allocated_storage       = 20
  storage_type            = "gp2"
  engine                  = "postgres"
  engine_version          = "12.5"
  instance_class          = "db.t2.micro"
  username                = var.DBUSERNAME
  password                = var.DBPASSWORD
  port                    = 5432
  publicly_accessible     = true
  availability_zone       = local.default_availability_zone
  security_group_names    = []
  vpc_security_group_ids  = ["sg-0cd10e64f08bee8cf"]
  parameter_group_name    = "default.postgres12"
  multi_az                = false
  backup_retention_period = 0
  backup_window           = "21:55-22:25"
  maintenance_window      = "sun:01:25-sun:01:55"
  skip_final_snapshot     = true
}

resource "null_resource" "lexibot-db-setup" {
  depends_on = [aws_db_instance.lexibot-db]

  provisioner "local-exec" {
    command     = "psql -h ${aws_db_instance.lexibot-db.address} -U ${var.DBUSERNAME} -f ${path.module}/scripts/create.sql"
    environment = {
      PGPASSWORD = var.DBPASSWORD
    }
  }
}

resource "aws_route53_zone" "lexibot-link-zone-public" {
  name    = local.domain_name
  comment = ""
}

resource "aws_route53_record" "lexibot-link-A" {
  zone_id = aws_route53_zone.lexibot-link-zone-public.zone_id
  name    = local.domain_name
  type    = "A"
  records = [aws_instance.lexibot-instance-main.public_ip]
  ttl     = "60"
}

resource "aws_route53_record" "www-lexibot-link-A" {
  zone_id = aws_route53_zone.lexibot-link-zone-public.zone_id
  name    = local.www_domain_name
  type    = "A"
  records = [aws_instance.lexibot-instance-main.public_ip]
  ttl     = "60"
}

// Write name servers to file.
resource "local_file" "name_servers" {
  content         = "${aws_route53_zone.lexibot-link-zone-public.name_servers[0]}\n${aws_route53_zone.lexibot-link-zone-public.name_servers[1]}\n${aws_route53_zone.lexibot-link-zone-public.name_servers[2]}\n${aws_route53_zone.lexibot-link-zone-public.name_servers[3]}"
  file_permission = "0644"
  filename        = "${path.module}/name_servers.txt"
}

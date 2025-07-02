# AMI de Ubuntu para instancias ECS
data "aws_ami" "ecs_optimized" {
  most_recent = true
  owners      = ["099720109477"] # Canonical/Ubuntu

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Key Pair para acceso SSH
resource "aws_key_pair" "this" {
  key_name   = "${var.app_name}-key"
  public_key = var.ssh_public_key
}

# Launch Configuration para instancias EC2
resource "aws_launch_configuration" "this" {
  name_prefix     = "${var.app_name}-"
  image_id        = data.aws_ami.ecs_optimized.id
  instance_type   = "t2.micro"
  security_groups = [aws_security_group.ecs.id]
  key_name        = aws_key_pair.this.key_name
  
  # Instalación y configuración de ECS en Ubuntu
  user_data = <<-EOF
              #!/bin/bash
              # Actualizar paquetes
              apt-get update
              apt-get install -y apt-transport-https ca-certificates curl software-properties-common

              # Instalar Docker
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
              add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
              apt-get update
              apt-get install -y docker-ce
              usermod -aG docker ubuntu
              
              # Instalar el agente de ECS
              mkdir -p /etc/ecs
              echo "ECS_CLUSTER=${aws_ecs_cluster.this.name}" >> /etc/ecs/ecs.config
              
              # Descargar e instalar el agente de ECS
              curl -o /tmp/ecs-agent.tar https://s3.amazonaws.com/amazon-ecs-agent/ecs-agent-latest.tar
              mkdir -p /tmp/ecs-agent
              tar -xf /tmp/ecs-agent.tar -C /tmp/ecs-agent
              
              # Iniciar el agente de ECS
              docker run --name ecs-agent \
                --detach=true \
                --restart=on-failure:10 \
                --volume=/var/run:/var/run \
                --volume=/var/log/ecs/:/log \
                --volume=/var/lib/ecs/data:/data \
                --volume=/etc/ecs:/etc/ecs \
                --net=host \
                --env-file=/etc/ecs/ecs.config \
                amazon/amazon-ecs-agent:latest
              EOF

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group para instancias EC2
resource "aws_autoscaling_group" "this" {
  name                 = "${var.app_name}-asg"
  launch_configuration = aws_launch_configuration.this.name
  min_size             = var.desired_capacity
  max_size             = var.desired_capacity * 2
  desired_capacity     = var.desired_capacity
  vpc_zone_identifier  = data.aws_subnets.default.ids

  tag {
    key                 = "Name"
    value               = "${var.app_name}-ecs-instance"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = ""
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Adjuntar el Auto Scaling Group al Target Group
resource "aws_autoscaling_attachment" "this" {
  autoscaling_group_name = aws_autoscaling_group.this.name
  lb_target_group_arn    = aws_lb_target_group.this.arn
}

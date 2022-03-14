#packer core first connects to plugins to fetch below required functionality
packer {
  required_plugins {
    amazon = {
      version = ">= 0.0.1"
      source  = "github.com/hashicorp/amazon"
    }
  }
}
variable "github_repo" {
  default = env("GITHUB_REPO_PATH")
}
#packer builder is able to create Amazon AMIs backed by EBS volumes for use in EC2
source "amazon-ebs" "ami-image" {
  ami_name      = "csye6225_ami_img_{{timestamp}}"
  instance_type = "t2.micro"
  source_ami_filter {
    filters = {
      virtualization-type = "hvm"
      name                = "amzn2-ami-kernel-5.10-hvm*"
      root-device-type    = "ebs"
    }
    owners      = ["amazon"]
    most_recent = true
  }
  launch_block_device_mappings {
    device_name           = "/dev/xvda"
    volume_type           = "gp2"
    volume_size           = "8"
    delete_on_termination = true
  }
  region       = "us-east-1"
  access_key   = "AKIAX6SPJCQYNQQ6RHKC"
  secret_key   = "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"
  ssh_username = "ec2-user"
}
build {
  sources = [
    "source.amazon-ebs.ami-image"
  ]
  provisioner "file" {
    destination = "/tmp/app.service"
    source      = "${var.github_repo}/packer/app.service"
  }
  provisioner "file" {
      destination = "/tmp/spring-boot-first-web-application-0.0.1-SNAPSHOT.jar"
      source      = "${var.github_repo}/target/spring-boot-first-web-application-0.0.1-SNAPSHOT.jar"
  }
  provisioner "shell" {
    inline = [
      "sleep 30",

		"sudo yum -y install java-11",
	        "sudo yum install maven -y",
               	"sudo yum update -y",
		"sudo yum -y install https://dev.mysql.com/get/mysql80-community-release-el7-5.noarch.rpm",
		"echo 'Install epel'",
		"sudo amazon-linux-extras install epel",
		"echo 'Install community server'",
		"sudo yum -y install mysql-community-server",
		"sudo systemctl enable --now mysqld",
		"systemctl status mysqld",
		"echo 'here'",
		"pass=$(sudo grep 'temporary password' /var/log/mysqld.log | awk {'print $13'})",
		"mysql --connect-expired-password -u root -p$pass -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY 'Shreekar_123';\"",
		"mysql -u root -pShreekar_123 -e \"create database users;\"",
		"pwd",
		"mkdir webapp-target",
		"cd webapp-target",
		"sudo cp /tmp/spring-boot-first-web-application-0.0.1-SNAPSHOT.jar spring-boot-first-web-application-0.0.1-SNAPSHOT.jar",
		"pwd",
		"ls",
		"sudo cp /tmp/app.service /etc/systemd/system/",
		"sudo systemctl enable --now app.service",
    ]
  }
}

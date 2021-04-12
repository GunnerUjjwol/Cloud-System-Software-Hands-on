terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {

  credentials = file("credentials.json")
  project = "ujjwol-project-terraform-intro"
  region = "europe-north1"
  zone = "europe-north1-a"
}

resource "google_compute_address" "vm_static_ip" {
  name = "ujjwol-terraform-ip"
}

resource "google_compute_network" "vpc_network" {
  name = "ujjwol-terraform-network"
}

resource "google_compute_instance" "vm_instance" {
  name = var.instance_name_input
  machine_type = "f1-micro"

  boot_disk {
    initialize_params {
      image = "ubuntu-1804-bionic-v20200317"
    }
  }

  network_interface {
    network = "default"
    access_config {
	nat_ip = google_compute_address.vm_static_ip.address
    }
  }
}

variable "instance_name_input" {}

output "instance_name" {
  value =  var.instance_name_input
}

output "public_ip" {
  value = google_compute_address.vm_static_ip.address
}
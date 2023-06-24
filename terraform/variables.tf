locals {
  data_lake_bucket = "data_lake_bus_data"
}

variable "project" {
  description = "Project ID"
  default     = "bus-data-389717"
  type        = string
}

variable "region" {
  description = "Region for GCP resources"
  default     = "southamerica-east1"
  type        = string
}

variable "zone" {
  description = "Zone"
  default     = "southamerica-east1-b"
  type        = string
}

variable "storage_class" {
  description = "Storage class type for your bucket"
  default     = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset"
  default     = ["busdata_bq", "dbt_busdata_stag", "dbt_busdata_prod"]
}

variable "vm_name" {
  description = "Name for VM instance"
  default     = "bus-data-instance"
  type        = string
}

variable "machine_type" {
  description = "Machine type for VM instance"
  default     = "e2-standard-4"
  type        = string
}

variable "vm_image" {
  description = "Image for VM instance"
  default     = "projects/debian-cloud/global/images/debian-11-bullseye-v20230509"
  type        = string
}
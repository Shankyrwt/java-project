module "cdc_etl" {
  count                            = local.enable_cdc_etl_pipeline ? 1 : 0
  source                           = "git::git@github.com:Vetted/certa-infra.git//terraform/modules/anytime_deployment?ref=v6.1.0"
  availability_zone                = local.availability_zone
  environment                      = local.environment
  region                           = local.region
  serverless_stage                 = "slackcart"
  application                      = "cdc-etl"
  shard_count                      = 4
  stream_retention_period          = 24
  batch_size                       = 10000
  batch_window                     = 5
  platform                         = "Krypton"
  cdc_max_retry_count              = 5
  cdc_lambda_timeout               = 900
  es_endpoint                      = local.es_endpoint
  es_index                         = local.es_wf_index
  es_api_key_id                    = local.es_api_key_id
  es_api_key_secret                = local.es_api_key_secret
  rds_hostname                     = "app-db.services.slackcart.com"
  rds_username                     = local.rds_db_username
  rds_password                     = local.rds_db_password
  rds_db_name                      = local.rds_db_name
  sentry_dsn                       = "https://e9166b07d0842fe73d82d8fb31c13552@o4382.ingest.us.sentry.io/4507168368885760"
  codebuild                = {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/standard:5.0"
    type                        = "LINUX_CONTAINER"
    build_timeout               = 15
    buildspec_location          = "buildspec.yml"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true
  }
  github = {
    branch = "development",
    owner  = "Vetted",
    repo   = "es_etl_cdc"
  }
  owned_by_team            = "backend"
  codestar_connection_name = local.codestar_connection_name

  dms_replication_instance = {
    engine_version = "3.5.1"
    instance_class = "dms.c5.large"
    storage        = 50
  }
  dms_serverless_replication_task_enabled = true
  dms_serverless_min_dcu = 4
  dms_serverless_max_dcu = 8
  replication_task_setting = {
    "parallel_apply_threads" : 12,
    "parallel_apply_buffer_size" : 1000,
    "parallel_apply_queues_per_thread" : 4,
    "stream_buffer_count" : 12,
    "stream_buffer_size_in_mb" : 32
    "log_level" : "DEFAULT"
  }
  schemas = ["abir", "swathi", "workatopoc", "nitindemo", "octanner", "mars", "sidharth", "templates", "flowserve", "pvg", "joysonsafety", "sanjeev", "stephencooke", "libertymutual", "shubhashish", "boxstudio", "ajinkya", "gabe", "roku", "neil", "hcstudio", "anupam", "honeywellduediligence", "risenow", "goexpedi", "goodyear", "warriors", "expedi", "amex", "mckmep", "ashwani", "shivam", "werfen", "grey", "white", "instacart", "himadri", "brendon", "tarak", "enrique", "rudrasish", "bhanuprakash", "grubhub", "vetted", "harshitha", "shachi", "usha", "juan", "abhijit", "tysers", "hima", "indeed", "cloudflare", "people", "generali", "abra", "risknavigatorbain", "wmappbuilder", "harshit", "mastec", "stephen", "mdias", "ajitv2", "revanth", "ge", "palak", "etsy", "dnb", "accenture", "yashsri", "pepsisanctions", "support", "cabansystems", "sauravtest", "aditee", "internal", "tidal", "square_bak", "sudhanshu", "box", "ayush", "shivani", "ajit", "aakash", "aman", "play", "bhanu", "ram", "zeeshan", "aditi", "hc", "squaresr", "karan", "otis", "risknavigatorbaindev", "mahip", "tanu", "rokupartners", "vishal", "pallavi", "martin", "balachandar", "pacvue", "mona", "accentureaml", "nikita", "boeingsuppliers", "apurv", "isha", "quantcast", "samarth", "honeywell", "boeing", "srm", "dnbdemo", "wwt", "uiplay", "uidemo", "uber", "visa", "fb", "mck", "divya", "astra", "cruise", "instacerta", "pepsi", "hashicorp", "square", "jag", "sree", "shreya", "squash", "siddharth", "subalakshmi", "gayatri"]
  tables  = ["krypton_response", "krypton_workflow"]
  columns = {
    krypton_response = ["id", "workflow_id", "deleted", "created_at", "updated_at", "field_tag", "answer", "attachment", "files", "groups_cache", "submitted_at"],
    krypton_workflow = ["id", "business_unit_id", "deleted", "created_by_id", "status_id", "region_id", "all_groups_cache", "name", "created_at", "definition_id", "updated_at", "lc_data"]
  }

  create_es_deployment = true
  es_deployment_config = {
    stage                  = "nonprod"
    deployment_template_id = "aws-general-purpose-arm-v7"
    region                 = "us-east-1"
    version                = "8.10.2"
    name                   = "nonprod-etl-elasticsearch"
    elasticsearch = {
      autoscale = true
      hot = {
        autoscaling = {
            max_size = "120g"
            max_size_resource = "memory"
        }
        size = "4g"
        size_resource = "memory"
        zone_count = 1
      }
    }
    kibana = {
      size = "1g"
      size_resource = "memory"
      zone_count = 1
    }
    enterprise_search = {
      size = "2g"
      size_resource = "memory"
      zone_count = 1
    }
    integrations_server = {
      "size": "1g",
      "size_resource": "memory",
      "zone_count": 1
    }
  }
  endpoint_service_name    = "com.amazonaws.vpce.us-east-1.vpce-svc-0e42e1e06ed010238"
  private_endpoint_subnets = [module.vpc.private_app_subnet_ids[2]]

  aws_sns_alerts_topic  = "certa-infra-alerts"
  slack_channel_id      = "C04GXA82MB4"
  slack_token_ssm_param = "/slack/certa-rockstars/alertbot/token"
  alerts_config = {
    dms_task_alerts_evaluation_period = 900
    dms_task_capacity_utilisation_threshold = 80
    dms_task_cdc_source_latency_threshold = 5
    dms_task_cdc_target_latency_threshold = 5

    kds_alerts_evaluation_period = 900
    kds_get_records_iterator_age_threshold = 2000
    kds_put_records_latency_threshold = 1000
    kds_get_records_latency_threshold = 1000

    lambda_alerts_evaluation_period = 900
    lambda_iterator_age_threshold = 10000
    lambda_errors_threshold = 1
  }

  providers = {
    aws = aws.backend
  }
}

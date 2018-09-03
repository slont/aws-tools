# AWS Tools
Implemented by Python3

## Environment
- **python**: 3.6.6
- **pip**: 18.0

### Dependencies
- **boto3**: AWS SDK for Python

## log-exporter

### How to use
#### format
`python log-exporter.py <profile> <log_groups> <start_at>`

- **profile**: Profile name from `~/.aws/credentials`
- **log_group**: CloudWatch Log Group Name
- **start_at**: The logs after the 'start_at' `YYYY-MM-DDTHH:mm:ss` (UTC) is exported

#### example
`python log-exporter.py project-prod '/aws/ecs/group_name' 2018-08-20T04:00:00 > /tmp/log.txt`

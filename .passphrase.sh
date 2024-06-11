#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "This script is intended to be sourced, not run directly."
  echo "Please source with this command: 'source ./.passphrase.sh'"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "jq could not be found, but is required."
  echo "See this link for how to install jq https://jqlang.github.io/jq/download/"
fi

# ACCOUNT_ID=$(aws sts get-caller-identity| jq -r '.Account')
# S3_BACKEND_BUCKET="s3://pulumi-backend-$ACCOUNT_ID"

GIT_ROOT=$(git rev-parse --show-toplevel)
# find the file from the git root that is .pulumi_passphrase_secret_name
SECRET_FILE=$(find "$GIT_ROOT" -name .pulumi_passphrase_secret_name)
SECRET_NAME=$(cat "$SECRET_FILE")
echo "using $SECRET_NAME as the secret name"
SECRET_VALUE=$(aws secretsmanager get-secret-value --secret-id "$SECRET_NAME" | jq -r '.SecretString')
PASSPHRASE=$(echo "$SECRET_VALUE" | jq -r '.PULUMI_CONFIG_PASSPHRASE')
S3_BACKEND_BUCKET=$(echo "$SECRET_VALUE" | jq -r '.bucket_name')
echo "using $S3_BACKEND_BUCKET as the bucket name"
# strip s3:// if it exists on the bucket name
S3_BACKEND_BUCKET=${S3_BACKEND_BUCKET#s3://}

pulumi login "s3://${S3_BACKEND_BUCKET}"
export PULUMI_CONFIG_PASSPHRASE=$PASSPHRASE

echo "Passphrase is now available for this session"

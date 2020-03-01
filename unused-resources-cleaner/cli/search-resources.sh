#!/bin/bash
# requires: awscli, jq

# assume role or use your aws credentials

OUTPUT=output
REPORT_FILE="${OUTPUT}/unused-resources-report-$(date +%Y-%m-%d-%H%M%S).txt"

if [ ! -d "${OUTPUT}" ]; then
    mkdir "${OUTPUT}";
fi

if [ ! -f "${REPORT_FILE}" ]; then
    touch "${REPORT_FILE}"
fi

REGIONS=$(aws ec2 describe-regions \
    --query Regions[].[RegionName] \
    --output text)

## EC2

# Find stopped EC2 instances and decide if they can be removed
echo "Stopped EC2 instances" >> "${REPORT_FILE}"

for region in ${REGIONS}; do

    INSTANCES=$(aws ec2 describe-instances \
        --output json \
        --region "${region}" | \
        jq -r ".Reservations[].Instances[] | select(.State.Code == 80) | \
        [.InstanceId, .InstanceType] | @tsv")

    if [ -n "$INSTANCES" ]; then
        echo "${region}" >> "${REPORT_FILE}"
        echo "${INSTANCES}" >> "${REPORT_FILE}"
    fi
done;
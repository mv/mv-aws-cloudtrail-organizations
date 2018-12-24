# vim:ft=make:ts=8:sts=8:sw=8:noet:tw=80:nowrap:list

# Cloudtrail
ORG_NAME="mv-organization"
TRAIL_NAME="org-trail"
S3_BUCKET="${ORG_NAME}-cloudtrail/${TRAIL_NAME}"

AWS_REGION=us-east-1

###
### tasks
###
.PHONY: help vars sample

all: help

help:
	@echo "Organization: [${ORG_NAME}]"
	@echo
	@echo "    make vars  - Defined vars for [${ORG_NAME}]"
	@echo
	@echo "    make sample - Cloudformation: sample"
	@echo


vars:
	@echo "Organization: [${ORG_NAME}]"
	@echo "CloudTrail:   [${TRAIL_NAME}]"
	@echo "S3 Bucket:    [${S3_BUCKET}]"

cs:
	aws cloudformation create-stack \
	    --stack-name ${ORG_NAME}-cloudtrail \
	    --template-body file://cloudtrail.sample-org-trail.yaml \
	    --region ${AWS_REGION}

us:
	aws cloudformation update-stack \
	    --stack-name ${ORG_NAME}-cloudtrail \
	    --template-body file://cloudtrail.sample-org-trail.yaml \
	    --region ${AWS_REGION}

vt:
	aws cloudformation validate-template  \
	    --template-body file://cloudtrail.sample-org-trail.yaml \
            --output text
ds:
	aws cloudformation delete-stack \
	    --stack-name ${ORG_NAME}-cloudtrail \
	    --region ${AWS_REGION}


is_org:
	aws cloudtrail  update-trail  \
	    --name sample-org-trail   \
	    --is-organization-trail   \
	    --region ${AWS_REGION}

no_org:
	aws cloudtrail  update-trail  \
	    --name sample-org-trail   \
	    --no-is-organization-trail \
	    --region ${AWS_REGION}



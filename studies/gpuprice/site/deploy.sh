#!/bin/bash
# Publish the gpuprice results page to https://gpu.invariant.team (stack gpuprice-site, AWS profile fuelos).
#   studies/gpuprice/site/deploy.sh          rebuild data.json from the result files, upload, refresh the cache
# The first run creates the stack (certificate, CloudFront, DNS records): about 5 minutes. Later runs take seconds.
# Remove everything: empty the bucket, then `aws --profile fuelos --region us-east-1 cloudformation delete-stack --stack-name gpuprice-site`.
set -euo pipefail
cd "$(dirname "$0")/../../.."
aws=(aws --profile fuelos --region us-east-1)
site=studies/gpuprice/site

"${aws[@]}" cloudformation deploy --stack-name gpuprice-site --template-file $site/template.yaml \
  --parameter-overrides DomainName=gpu.invariant.team HostedZoneId=Z102362032K546X2IQJG1 \
  --tags project=gpuprice-site --no-fail-on-empty-changeset
out() { "${aws[@]}" cloudformation describe-stacks --stack-name gpuprice-site --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }

python3 $site/build.py
for f in index.html data.json favicon.svg; do
  [ -f $site/$f ] && "${aws[@]}" s3 cp --only-show-errors --cache-control no-cache $site/$f "s3://$(out Bucket)/$f"
done
"${aws[@]}" cloudfront create-invalidation --distribution-id "$(out Distribution)" --paths '/*' --query Invalidation.Status --output text
out Url

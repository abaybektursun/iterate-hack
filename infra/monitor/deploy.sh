#!/bin/bash
# Deploy or redeploy the board page (tools/view.py) to AWS: the stack iterate-monitor, then the code.
#   infra/monitor/deploy.sh                                   first deploy, and every redeploy
#   infra/monitor/deploy.sh monitor.<domain> <hosted zone id>  also attach the custom domain (kept on later runs)
set -euo pipefail
cd "$(dirname "$0")/../.."
aws=(aws --profile fuelos --region us-east-1)

overrides=()
if [ $# -gt 0 ]; then
  overrides=(--parameter-overrides "DomainName=$1" "HostedZoneId=$2")
fi
"${aws[@]}" cloudformation deploy --stack-name iterate-monitor --template-file infra/monitor/template.yaml \
  --capabilities CAPABILITY_NAMED_IAM --tags project=iterate-monitor --no-fail-on-empty-changeset ${overrides[@]+"${overrides[@]}"}

build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT
# all of tools/*.py (a few kB), so a new import in view.py needs no change here; boto3 comes with the Lambda runtime;
# the paper PDF that view.py serves at /paper/the-finish-dial.pdf lies beside the code
zip -q -j "$build/code.zip" tools/*.py infra/monitor/run.sh studies/rlneurons/paper/the-finish-dial.pdf
"${aws[@]}" lambda update-function-code --function-name iterate-monitor --zip-file "fileb://$build/code.zip" \
  --query CodeSha256 --output text
"${aws[@]}" lambda wait function-updated-v2 --function-name iterate-monitor

"${aws[@]}" cloudformation describe-stacks --stack-name iterate-monitor \
  --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' --output text

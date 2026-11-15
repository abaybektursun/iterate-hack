#!/bin/bash
# Deploy or redeploy the board page (tools/view.py) to AWS: the stack iterate-monitor, then the code.
#   infra/monitor/deploy.sh                                   first deploy, and every redeploy
#   infra/monitor/deploy.sh monitor.<domain> <hosted zone id>  also attach the custom domain (kept on later runs)
#   infra/monitor/deploy.sh monitor.<domain> <hosted zone id> <domain>  and the home page's domain, in the same zone
set -euo pipefail
cd "$(dirname "$0")/../.."
aws=(aws --profile fuelos --region us-east-1)

# the paper PDFs: the files view.PAPERS serves, read by importing view.py, so a view.py that fails at import stops the
# deploy here, before anything is shipped, and a new paper is registered in view.PAPERS alone
papers=$(uv run -q --with boto3 python3 -c "import sys; sys.path.insert(0, 'tools'); import view; from pathlib import Path
print(' '.join(str(p[1].relative_to(Path.cwd())) for p in view.PAPERS.values()))")

overrides=()
if [ $# -gt 0 ]; then
  overrides=(--parameter-overrides "DomainName=$1" "HostedZoneId=$2" "HomeDomainName=${3-}")
fi
"${aws[@]}" cloudformation deploy --stack-name iterate-monitor --template-file infra/monitor/template.yaml \
  --capabilities CAPABILITY_NAMED_IAM --tags project=iterate-monitor --no-fail-on-empty-changeset ${overrides[@]+"${overrides[@]}"}

build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT
# all of tools/*.py (a few kB), so a new import in view.py needs no change here; boto3 comes with the Lambda runtime;
# the paper PDFs that view.py serves at /paper/<name>.pdf lie beside the code
zip -q -j "$build/code.zip" tools/*.py infra/monitor/run.sh $papers
# the site lab's pages and data (view.py serves them at /lab/), with their folders kept
(cd studies && zip -q -r "$build/code.zip" sitelab/index.html sitelab/prototypes -i '*/index.html' '*/data.json')
"${aws[@]}" lambda update-function-code --function-name iterate-monitor --zip-file "fileb://$build/code.zip" \
  --query CodeSha256 --output text
"${aws[@]}" lambda wait function-updated-v2 --function-name iterate-monitor

"${aws[@]}" cloudformation describe-stacks --stack-name iterate-monitor \
  --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' --output text

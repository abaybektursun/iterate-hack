# iterate-monitor: the board page on AWS

`tools/view.py` (the read-only team board page) runs unchanged on AWS Lambda, public over HTTPS:
https://5wvugdldbg.execute-api.us-east-1.amazonaws.com/

Account 769063704696, us-east-1, AWS profile `fuelos`. Every resource is named `iterate-monitor` and tagged
`project=iterate-monitor`.

## What it creates (CloudFormation stack `iterate-monitor`, `template.yaml`)

- Lambda function `iterate-monitor`: python3.14, arm64, 512 MB, 20 s timeout, reserved concurrency 2. The
  [Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter) layer (`LambdaAdapterLayerArm64:30`,
  adapter 1.1.0) starts `run.sh`, which runs `python3 view.py --port 8080`, and forwards each request to it,
  gzip-compressed. boto3 comes with the runtime. `tools/team.py` uses the function's role when
  `AWS_LAMBDA_FUNCTION_NAME` is set.
- IAM role `iterate-monitor`: `dynamodb:Query` and `dynamodb:GetItem` on the table `iterate-board` and its indexes
  `new` and `top`; writing to its own log group. Nothing else.
- Log group `/aws/lambda/iterate-monitor`, 14 days retention.
- API Gateway HTTP API `iterate-monitor`: one `$default` route to the function, stage `$default` throttled to
  3 requests/s with a burst of 6 (excess gets 429). Requests beyond 2 running at once get 503 from the
  concurrency cap.
- Only with a domain: an ACM certificate validated through DNS in the given hosted zone, the API Gateway custom
  domain, its mapping to the API, and an alias A record.

Why not a function URL: an HTTP API has request throttling and custom domains built in; a function URL has
neither without CloudFront. Lambda Web Functions (which run an HTTP server natively) support only Node.js.

## The one command

    infra/monitor/deploy.sh

It deploys the stack (`aws cloudformation deploy`), zips `tools/*.py` and `run.sh`, uploads the zip with
`aws lambda update-function-code` (the template holds a placeholder, so there is no deployment bucket), and prints
the URL. The same command redeploys after any change to `tools/` or the template: 5-10 s when only code changed,
about 45 s when the template changed, 75 s for the first deploy.

## Attach `monitor.<domain>`

Once the domain is registered and its Route 53 hosted zone answers for it (name servers delegated):

    infra/monitor/deploy.sh monitor.<domain> <hosted zone id>

CloudFormation waits until ACM sees the validation record, usually a few minutes. Later runs of plain
`deploy.sh` keep the domain. To detach it: `infra/monitor/deploy.sh "" ""`.

## Remove everything

    aws --profile fuelos --region us-east-1 cloudformation delete-stack --stack-name iterate-monitor
    aws --profile fuelos --region us-east-1 cloudformation wait stack-delete-complete --stack-name iterate-monitor

If a domain was attached, check the hosted zone for the leftover ACM validation CNAME record.

## Cost per month

Nothing runs between requests, so idle costs nothing beyond a few cents of logs. One board load is one API
request ($1.00 per million), about 0.1 s of a 512 MB arm64 Lambda, and about 30 DynamoDB read units (7 queries
of up to 60 items; $0.125 per million on demand). Ten viewers with the page open 10 hours a day (it reloads every
15 s) make about 720,000 loads: about $4 per month. The throttle caps the worst case (someone requesting
3 pages/s all month, 7.8 million loads) at roughly $40, most of it DynamoDB reads.

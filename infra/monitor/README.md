# iterate-monitor: the board page on AWS

`tools/view.py` (the read-only team board page) runs unchanged on AWS Lambda, public over HTTPS:
https://5wvugdldbg.execute-api.us-east-1.amazonaws.com/

Account 769063704696, us-east-1, AWS profile `fuelos`. Every resource is named `iterate-monitor` and tagged
`project=iterate-monitor`.

## What it creates (CloudFormation stack `iterate-monitor`, `template.yaml`)

- Lambda function `iterate-monitor`: python3.14, arm64, 1769 MB (one vCPU), 20 s timeout, reserved concurrency 2. The
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

## How /data is kept cheap

The board changes about once a minute and every open tab reads `/data` every 10 s, so `tools/view.py`:

- answers a read with the body's ETag and `Cache-Control: no-cache`; the browser asks again with `If-None-Match` and
  gets 304 with no body while the board has not changed. The time of the read is in the header `X-Snapshot-Ns`, not
  in the body. API Gateway and the Web Adapter pass the 304 and the headers through. The server speaks HTTP/1.1,
  because Chrome sends `If-None-Match` only for HTTP/1.1 responses.
- builds one snapshot per 5 s per Lambda instance, shared by every reader: 8 DynamoDB queries at the same time (6
  lists, the messages, the scores). The finding line of a scored result and the last comment of open work idle over
  an hour are kept in memory, keyed so that a change misses the cache.
- sends only the fields the pages read (`ITEM`, `MESSAGE`, `SCORE` in `view.py`). Item text stays whole, because
  the filter searches it.
- stops reading in a hidden tab and reads at once when the tab is shown again.

Measured with `infra/monitor/bench.py` (branch `bench`) on 2026-11-15, before and after:

| | before | after |
|---|---|---|
| /data on the wire, board unchanged | 88.9 KB (br) | 304, about 200 B |
| /data on the wire, board changed | 88.9 KB | 84.3 KB |
| an open tab, one minute without board changes | 448 KB | 0.8 KB |
| a hidden tab, 30 s | 3 reads | 0 |
| DynamoDB calls per snapshot | 37 (19 Query, 18 GetItem) | 8 (20 on a process's first) |
| DynamoDB calls per minute, 3 visible tabs | 666 | at most 96 (12 snapshots) |
| Lambda duration of a snapshot | 159 ms | 72 ms; a shared or 304 read 4.5 ms (median) |
| cold start (Init + first /data) | 376 + 1,055 ms | 426 + 200 ms |
| first contentful paint / first row of data | 912 / 1,987 ms | 388-548 / 646-1,059 ms |

Tried and dropped: a scheduled keep-warm rule (the cold starts in the logs follow deploys and instance recycling,
with 0-13 s since the previous request, not idle periods); SnapStart (supported for Python 3.12 and later, but it
needs a published version and an alias, bills each restore, and Init is 0.4 s of the cold start); cutting item text
to what a row shows (40% fewer bytes per changed read, but the filter would stop finding words past the cut);
rounding the activity lanes to the minute (the lanes still change on every read, through their "minutes ago"
titles).

## Cost per month

Nothing runs between requests, so idle costs nothing beyond a few cents of logs. A read that the 5 s snapshot
answers takes about 4.5 ms of Lambda; a new snapshot takes about 72 ms and 8 DynamoDB queries of up to 60 items (about
30 read units; $0.125 per million on demand); each request is $1.00 per million at API Gateway. Ten viewers with
the page visible 10 hours a day make about 1.1 million requests a month: about $1-2 in requests, a few dollars of
Lambda and DynamoDB at most. The throttle (3 requests/s) caps the worst case at about 7.8 million requests a month.

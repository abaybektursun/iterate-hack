#!/bin/bash
# Lambda handler: the Lambda Web Adapter layer (AWS_LAMBDA_EXEC_WRAPPER=/opt/bootstrap) runs this script, then
# forwards each HTTP request to 127.0.0.1:$AWS_LWA_PORT. view.py runs unchanged. HOME=/tmp because Lambda sets no
# home directory and team.CACHE is built from it (the page itself never writes there).
cd "$LAMBDA_TASK_ROOT"
HOME=/tmp PYTHONUNBUFFERED=1 exec python3 view.py --port "$AWS_LWA_PORT"

#!/bin/bash
# bash meta/reviews/abaybektursun/20261115-1920-paper4/deploy_gate.sh <deploy.sh revision, e.g. f09cf73, or WORK for the working file>
# Runs that revision's infra/monitor/deploy.sh on a copy of the tree with `aws` stubbed (prints its call), twice:
# with view.py as is, and with view.py failing at import (the 19:13 failure). Prints whether the Lambda code was shipped
# and which PDFs went into the zip.
set -u
rev=$1; src=$(git rev-parse --show-toplevel)
for mode in clean broken; do
  t=$(mktemp -d); mkdir -p "$t/bin" "$t/infra/monitor"
  cp -r "$src/tools" "$t/"; (cd "$src" && git ls-files 'studies/*.pdf' 'studies/sitelab/*' | cpio -pdm --quiet "$t")
  if [ "$rev" = WORK ]; then cp "$src/infra/monitor/deploy.sh" "$t/infra/monitor/"; else git -C "$src" show "$rev:infra/monitor/deploy.sh" > "$t/infra/monitor/deploy.sh"; fi; cp "$src/infra/monitor/run.sh" "$t/infra/monitor/"
  printf '#!/bin/bash\necho "aws $*" >> %s/aws.log\nfor a; do case $a in fileb://*) unzip -Z1 "${a#fileb://}" | grep -c "pdf$" > %s/pdfs;; esac; done\n' "$t" "$t" > "$t/bin/aws"; chmod +x "$t/bin/aws"
  [ $mode = broken ] && echo 'raise AssertionError("view.py fails at import")' >> "$t/tools/view.py"
  (cd "$t" && PATH="$t/bin:$PATH" bash infra/monitor/deploy.sh >/dev/null 2>&1); code=$?
  shipped=$(grep -c "lambda update-function-code" "$t/aws.log" 2>/dev/null || echo 0)
  echo "rev $rev view.py $mode: exit $code, lambda code shipped $shipped time(s), PDFs in zip $(cat "$t/pdfs" 2>/dev/null || echo none)"
  rm -rf "$t"
done

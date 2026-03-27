report:
  #!/usr/bin/env bash
  set -x
  if [ -z "$SINCE" ]; then
    SINCE=$(date -d '7 days ago' +%Y-%m-%d)
  fi
  args=(--since "$SINCE")
  if [ -n "$AUTHOR" ]; then
    args+=(--author "$AUTHOR")
  fi
  python main.py "${args[@]}"

my-report:
  #!/usr/bin/env bash
  set -x
  if [ -z "$SINCE" ]; then
    SINCE=$(date -d '7 days ago' +%Y-%m-%d)
  fi
  python main.py --since "$SINCE" --author "$(git config get user.name)"

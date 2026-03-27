report:
  #!/usr/bin/env bash
  if [ -z "$since" ]; then
    since=$(date -d '7 days ago' +%Y-%m-%d)
  fi
  python main.py --since "$since"

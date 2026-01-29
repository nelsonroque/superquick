# superquick

## Installation
```bash
uv pip install git+https://github.com/nelsonroque/superquick.git
```

## TOOD:

JSON export shouldnt have file count (breaks json syntax)
Add payload creator
Add --slack-webhook $URL
Add --teams-webhook $URL

```
if slack_webhook:
    status, body = http_post_json(slack_webhook, build_slack_payload(summary))
    if status >= 300:
        raise typer.Exit(code=2)

if teams_webhook:
    status, body = http_post_json(
        teams_webhook, build_teams_payload("sq results", summary)
    )
    if status >= 300:
        raise typer.Exit(code=2)

```
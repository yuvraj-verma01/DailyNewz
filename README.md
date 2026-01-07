# Daily Digest Bot

Command-line tool that fetches RSS news, ranks stories for World and India, creates concise summaries from RSS descriptions, renders an HTML email, saves it locally, and optionally emails it via Gmail SMTP.

## Setup

```bash
python -m venv .venv
```

```bash
# Windows
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate
```

```bash
pip install -e .[dev]
```

## Gmail App Password

1. Enable 2-Step Verification for your Google account.
2. Go to Google Account > Security > App passwords.
3. Create an app password for "Mail" on your device.
4. Set it as `GMAIL_APP_PASSWORD` in your environment.

## Example config.yaml

```yaml
world_feeds:
  - name: BBC World
    url: https://feeds.bbci.co.uk/news/world/rss.xml
  - name: Reuters World
    url: https://feeds.reuters.com/Reuters/worldNews
india_feeds:
  - name: The Hindu National
    url: https://www.thehindu.com/news/national/feeder/default.rss
  - name: Indian Express India
    url: https://indianexpress.com/section/india/feed/
source_weights:
  BBC World: 1.0
  Reuters World: 1.1
  The Hindu National: 1.0
  Indian Express India: 0.95
keywords:
  - election
  - conflict
  - diplomacy
  - economy
  - policy
email:
  from_email: sender@example.com
  to_email: recipient@example.com
  subject_prefix: Daily Digest
  smtp_host: smtp.gmail.com
  smtp_port: 465
output_dir: out
```

## Run once

```bash
python -m daily_digest_bot --config config.yaml --dry-run
```

```bash
python -m daily_digest_bot --config config.yaml
```

Environment variables:

- `GMAIL_APP_PASSWORD` (required to send)
- `DIGEST_FROM_EMAIL` (optional override)
- `DIGEST_TO_EMAIL` (optional override)

## Scheduling

### cron (Linux/macOS) at 08:00 Asia/Kolkata

1. Convert to UTC if your server is in UTC. 08:00 IST = 02:30 UTC.
2. Add a crontab entry:

```bash
crontab -e
```

```cron
30 2 * * * /path/to/project/.venv/bin/python -m daily_digest_bot --config /path/to/project/config.yaml
```

### Windows Task Scheduler

1. Open Task Scheduler > Create Task.
2. Trigger: Daily at 08:00.
3. Action: Start a program:
   - Program/script: `C:\\Path\\To\\project\\.venv\\Scripts\\python.exe`
   - Add arguments: `-m daily_digest_bot --config C:\\Path\\To\\project\\config.yaml`
4. Set "Start in" to the project directory.

## Troubleshooting

- RSS failures: Some feeds block frequent requests; reduce frequency or add more sources.
- Timeouts: Check network access and increase the timeout in `feeds.py` if needed.
- Gmail auth errors: Make sure you are using an App Password, and the `from_email` matches the authenticated account.
- Empty results: Verify feed URLs and confirm they are valid RSS feeds.

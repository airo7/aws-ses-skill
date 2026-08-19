# aws-ses-skill

**Amazon SES skill for any agent / harness: sandbox → production access, domain/DKIM/SPF setup, SMTP credentials, and newsletter (Sendy) integration.**

> **Author:** abebe — [@airo77](https://x.com/airo77)

A battle-tested playbook that takes a fresh AWS account to a working,
production-capable email setup — including the exact support-case strategy
that gets **production access GRANTED** (the step most guides gloss over).

Works with Hermes Agent, Claude Code, Codex, Cursor, OpenCode, OpenClaw, and
any other tool that loads a `SKILL.md`. The scripts are plain `python3` +
`boto3` — no Hermes runtime required.

---

## Why this skill exists

Getting out of the SES **sandbox** is the hard part. Most people get
rejected — often multiple times — for reasons AWS never explains clearly:

- **Wrong mail type** — the #1 rejection cause. Marketing/bulk sends MUST be
  classified as `MARKETING`, not `TRANSACTIONAL`.
- **Vague use-case descriptions** — AWS wants specifics: website, signup flow,
  volume, opt-in mechanism.
- **No bounce/complaint plan** — they want to see automatic suppression
  handling.

This skill encodes the exact answers that work, plus the scripts to verify
your setup at every step.

---

## What it covers

- **Step 1** — Prerequisites & credentials
- **Step 2** — Account status check (sandbox vs production, quota, review)
- **Step 3** — Domain verification + DKIM + SPF (with DNS troubleshooting)
- **Step 4** — Production access playbook (the critical part)
- **Step 5** — SMTP credential generation
- **Step 6** — Sending a test email
- **Step 7** — Sendy newsletter integration (worked example)
- **Step 8** — SNS bounce & complaint handling
- **Step 9** — Newsletter sending strategy (warmup, rate limits, hygiene)
- **Step 10** — Troubleshooting
- **Step 11** — Cost estimation

---

## Scripts

- `scripts/check_ses_status.py` — account, domain, DKIM health check (JSON output)
- `scripts/gen_smtp_password.py` — derive SES SMTP password from IAM secret
- `scripts/verify_dns.py` — verify DKIM CNAMEs + SPF records (`dig`)
- `scripts/send_test_email.py` — send a test email (`--dry-run` safe)
- `scripts/setup_domain.py` — verify domain + print DNS records (`--dry-run` safe)
- `scripts/bounce_stats.py` — bounce/complaint/suppression stats

All scripts:

- read credentials from the standard boto3 credential chain
- `send_test_email.py` and `setup_domain.py` support `--dry-run` (preview without network calls)
- are safe to run against any account — nothing destructive

---

## Templates

`templates/support-case-reply.md` — the complete AWS Support case kit:

- **Part A — Initial Request:** open the production-access case (get approved
  the first time)
- **Part B — Follow-Up Reply:** respond when DENIED or stuck PENDING
  (same case thread — never open a duplicate)

---

## Installation

Clone once, then drop the folder where your agent looks for skills. The
playbook lives in `SKILL.md`; scripts stay next to it.

```bash
git clone https://github.com/airo7/aws-ses-skill.git
```

### Hermes Agent

```bash
hermes skills install https://raw.githubusercontent.com/airo7/aws-ses-skill/main/SKILL.md
# or from ClawHub:
hermes skills install airo7/aws-ses-skill
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r aws-ses-skill ~/.claude/skills/aws-ses
# or project-local:
mkdir -p .claude/skills
cp -r aws-ses-skill .claude/skills/aws-ses
```

### OpenAI Codex CLI

```bash
mkdir -p ~/.codex/skills
cp -r aws-ses-skill ~/.codex/skills/aws-ses
```

### Cursor

```bash
mkdir -p .cursor/skills
cp -r aws-ses-skill .cursor/skills/aws-ses
```

### OpenCode / OpenClaw / any SKILL.md agent

```bash
# OpenCode
mkdir -p .opencode/skills
cp -r aws-ses-skill .opencode/skills/aws-ses

# OpenClaw / ClawHub
# listing: https://clawhub.ai/airo7/skills/aws-ses-skill
```

### No agent — just the scripts

```bash
cd aws-ses-skill
python3 -m pip install boto3
python3 scripts/check_ses_status.py yourdomain.com
```

Restart the agent (or start a new session) so it re-scans skills.

---

## Quick start

```bash
# 1. Check where you stand (sandbox or production?)
python3 scripts/check_ses_status.py yourdomain.com

# 2. Verify the domain in SES, then add the printed DNS records
python3 scripts/setup_domain.py yourdomain.com --dry-run   # preview first
python3 scripts/setup_domain.py yourdomain.com

# 3. Confirm DNS propagated
python3 scripts/verify_dns.py yourdomain.com

# 4. Request production access (see SKILL.md §4 + the case templates)

# 5. Generate SMTP credentials (reads the secret from the boto3 credential
#    chain — never pass the secret on the command line)
python3 scripts/gen_smtp_password.py --region eu-north-1

# 6. Send a test email
python3 scripts/send_test_email.py --from sender@yourdomain.com \
    --to you@example.com --subject "Hello" --body "Test" --dry-run
```

---

## Tests

Fully mocked — no AWS calls, no credentials, no network:

```bash
python3 -m unittest tests.test_aws_ses -v
# 26 tests, all pass
```

---

## Requirements

- Python 3.11+
- `boto3` (AWS SDK)
- `dig` (dnsutils/bind-tools) — only for `verify_dns.py`
- Valid AWS credentials in the standard chain (environment variables,
  shared credentials file, or IAM role)

---

## Disclaimer

This skill is provided as-is, without warranty of any kind. AWS APIs and
pricing change — verify critical steps (production-access criteria, sending
limits, free-tier terms) against the current AWS documentation before acting.
Email is a reputation-sensitive channel: you are responsible for your own
sending practices, bounce/complaint hygiene, and compliance.

## Found a bug?

Please open a pull request. This is a community-maintained skill — if a script
fails, returns wrong data, or an AWS API has drifted, a PR fixing it is very
welcome. Include the AWS error you hit (redacting any account IDs or keys) so
it can be reproduced.

---

## License

MIT

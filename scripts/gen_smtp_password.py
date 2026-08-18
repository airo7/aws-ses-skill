"""derive an ses smtp password from an iam secret key.

the password is not the raw iam secret — it is a sigv4-style derivation:
  1. sign "11111111" with HMAC-SHA256 keyed by "AWS4" + secret
  2. chain through region, "ses", "aws4_request"
  3. sign the literal "SendRawEmail"
  4. base64-encode a 0x04 version byte prepended to that signature

the smtp username is the iam access key id. region is REQUIRED — the
derived password differs per region.
see: https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html
"""

import argparse
import base64
import hashlib
import hmac
import os
import sys

import boto3


def derive_smtp_password(iam_secret: str, region: str) -> str:
    """derive the ses smtp password for an iam secret and region."""
    if not iam_secret:
        raise ValueError("IAM secret key must not be empty")
    if not region:
        raise ValueError("region is required for smtp password derivation")

    def _sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    signature = _sign(("AWS4" + iam_secret).encode("utf-8"), "11111111")
    signature = _sign(signature, region)
    signature = _sign(signature, "ses")
    signature = _sign(signature, "aws4_request")
    signature = _sign(signature, "SendRawEmail")

    return base64.b64encode(bytes([0x04]) + signature).decode("ascii")


def _resolve_credentials(secret: str | None) -> tuple[str, str]:
    """resolve (iam_secret, iam_key_id) from --secret or the boto3 chain.

    prefers the explicit --secret flag; otherwise falls back to the standard
    boto3 credential chain. never prints or sends the secret anywhere.
    """
    if secret:
        # key id only available from the chain; may be None if only --secret given.
        try:
            creds = boto3.Session().get_credentials()
            key_id = creds.access_key if creds else None
        except Exception:
            key_id = None
        return secret, key_id

    creds = boto3.Session().get_credentials()
    if not creds or not creds.secret_key:
        raise ValueError(
            "No IAM secret available. Pass --secret or configure the "
            "standard AWS credential chain (environment variables, "
            "shared credentials file, or an IAM role)."
        )
    return creds.secret_key, creds.access_key


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive an SES SMTP password from an IAM secret key."
    )
    parser.add_argument(
        "--secret",
        help="IAM Secret Access Key (falls back to the boto3 credential chain)",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWS region for the SMTP endpoint (required; also read from AWS_DEFAULT_REGION)",
    )
    args = parser.parse_args()

    region = args.region or os.getenv("AWS_DEFAULT_REGION")
    if not region:
        print("ERROR: region is required. Pass --region or set AWS_DEFAULT_REGION.", file=sys.stderr)
        sys.exit(1)

    try:
        iam_secret, iam_key_id = _resolve_credentials(args.secret)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    smtp_password = derive_smtp_password(iam_secret, region)

    print(f"SMTP_USERNAME: {iam_key_id or '<not resolved>'}")
    print(f"SMTP_PASSWORD: {smtp_password}")
    print(f"SMTP_SERVER:   email-smtp.{region}.amazonaws.com")
    print(f"SMTP_PORT:     587")


if __name__ == "__main__":
    main()

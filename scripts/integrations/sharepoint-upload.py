#!/usr/bin/env python3
"""sharepoint-upload.py — upload file a SharePoint via Microsoft Graph.

Richiede app registration in Azure AD con Files.ReadWrite.All + Sites.ReadWrite.All.

Usage:
    export MSGRAPH_TENANT=tenant.onmicrosoft.com
    export MSGRAPH_CLIENT_ID=...
    export MSGRAPH_CLIENT_SECRET=...
    export MSGRAPH_SITE_ID=...              # ID del site SharePoint
    sharepoint-upload.py <file.pdf> --folder "Documenti/Proposte"
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request


def get_token():
    tenant = os.environ.get("MSGRAPH_TENANT")
    cid = os.environ.get("MSGRAPH_CLIENT_ID")
    secret = os.environ.get("MSGRAPH_CLIENT_SECRET")
    if not (tenant and cid and secret):
        print("[ERR] set MSGRAPH_TENANT, MSGRAPH_CLIENT_ID, MSGRAPH_CLIENT_SECRET", file=sys.stderr)
        sys.exit(2)
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": secret,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8")).get("access_token")


def upload(file_path, folder):
    site = os.environ.get("MSGRAPH_SITE_ID")
    if not site:
        print("[ERR] set MSGRAPH_SITE_ID", file=sys.stderr)
        sys.exit(2)
    token = get_token()
    p = pathlib.Path(file_path)
    enc_path = urllib.parse.quote(f"{folder}/{p.name}")
    url = f"https://graph.microsoft.com/v1.0/sites/{site}/drive/root:/{enc_path}:/content"
    req = urllib.request.Request(url, data=p.read_bytes(), method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--folder", default="Documenti")
    args = ap.parse_args()
    result = upload(args.file, args.folder)
    print(f"[OK] uploaded: {result.get('webUrl', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

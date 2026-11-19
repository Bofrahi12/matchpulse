#!/bin/bash
# Almalaeb V2 — deploy to Render once the GitHub repo exists.
# Prerequisite (user, 1 min): create EMPTY repo Bofrahi12/almalaeb-v2 on github.com.
# Then run: bash tools/deploy-render.sh
# Do NOT run before the repo exists — gh-push-dir bootstrap 404s otherwise.
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=/opt/muse/skills/custom-connector-setup/bin

echo "== 1. Push to GitHub =="
python3 ~/workspace/custom-connectors/custom.legacy-github/bin/gh-push-dir.py \
  --dir . --repo Bofrahi12/almalaeb-v2 --branch main

echo "== 2. Render owner id =="
OWNER=$(python3 ~/workspace/custom-connectors/custom.legacy-render/bin/render-svc.py owners \
  | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['id'])")
echo "owner: $OWNER"

echo "== 3. Create Render static site (skip if it already exists) =="
python3 ~/workspace/custom-connectors/custom.legacy-render/bin/render-svc.py \
  create-static almalaeb https://github.com/Bofrahi12/almalaeb-v2 "$OWNER" main . \
  || echo "(create-static failed — check render-svc.py list; service may already exist)"

echo "== 4. After first deploy, replace placeholder domain =="
echo "Get the live URL from Render dashboard, then:"
echo "  sed -i 's/almalaeb.example.com/<real-domain>/g' sitemap.xml robots.txt"
echo "  re-push (step 1 again) and trigger a Render deploy."
echo "== 5. Verify =="
echo "  curl -s -o /dev/null -w '%{http_code}\n' https://almalaeb.onrender.com/"
echo "  curl -s https://almalaeb.onrender.com/sitemap.xml | head"

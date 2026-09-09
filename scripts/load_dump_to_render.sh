#!/usr/bin/env bash
# Load database/final.sql into a Render Postgres instance.
#
# Usage:
#   ./scripts/load_dump_to_render.sh "postgresql://user:pass@host/eventflow"
#
# Get that connection string from the Render dashboard -> your eventflow-db
# -> "External Connection String" (needed since you're running this from
# your own machine, not from inside Render's network).
#
# Note: database/final.sql contains `ALTER TABLE ... OWNER TO postgres`
# statements left over from the original pg_dump. Render assigns its own
# username (not literally "postgres"), so those specific lines will print
# errors — that's expected and harmless. psql continues past them and
# every table still gets created and owned by your Render user correctly.
# Do NOT add --set ON_ERROR_STOP=1, or the load will abort on those lines.

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <render-external-connection-string>" >&2
  exit 1
fi

DB_URL="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DUMP_FILE="$SCRIPT_DIR/../database/final.sql"

echo "Loading $DUMP_FILE into $DB_URL"
echo "(Ownership-related errors below are expected — see script comments.)"
echo

psql "$DB_URL" -f "$DUMP_FILE"

echo
echo "Done. Sanity-check with:"
echo "  psql \"$DB_URL\" -c 'select count(*) from events;'"

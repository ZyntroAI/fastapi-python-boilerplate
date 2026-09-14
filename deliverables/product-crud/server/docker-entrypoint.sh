#!/bin/sh
#
# Entrypoint for the product-crud API image.
#
# Applies the Prisma schema before starting the server, then execs the CMD so
# signals reach the Node process directly (tini is PID 1 and forwards them).
#
# Prisma has two ways to bring a database up to date:
#   - migrate deploy : replays committed migrations. Needs prisma/migrations/.
#   - db push        : diffs the schema straight onto the database.
#
# This project has no committed migrations, so `migrate deploy` would be a
# silent no-op that leaves the tables missing. The script therefore picks
# `migrate deploy` only when a migrations directory is actually present, and
# falls back to `db push` otherwise.
#
# Override with SCHEMA_SYNC=none to skip entirely (e.g. when a release job
# applies the schema out of band).
set -e

echo "applying database schema (SCHEMA_SYNC=${SCHEMA_SYNC:-auto})"

if [ "${DATABASE_URL}" = "" ]; then
  echo "ERROR: DATABASE_URL is not set" >&2
  exit 1
fi

case "${SCHEMA_SYNC:-auto}" in
  none)
    echo "schema sync skipped (SCHEMA_SYNC=none)"
    ;;
  push)
    npx prisma db push --skip-generate
    ;;
  deploy)
    npx prisma migrate deploy
    ;;
  auto)
    if [ -d prisma/migrations ]; then
      echo "found prisma/migrations - running migrate deploy"
      npx prisma migrate deploy
    else
      echo "no prisma/migrations - running db push"
      npx prisma db push --skip-generate
    fi
    ;;
  *)
    echo "ERROR: unknown SCHEMA_SYNC value '${SCHEMA_SYNC}' (expected auto|deploy|push|none)" >&2
    exit 1
    ;;
esac

echo "starting: $*"
exec "$@"

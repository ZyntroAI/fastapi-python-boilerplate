# ============================================
banner "07. Supabase PostgREST Schema Check"
# ============================================
if command -v psql &>/dev/null && [ -n "$DATABASE_URL" ]; then
  if psql "$DATABASE_URL" -c "\dn" | grep -q "pgrst_no_exposed_schemas"; then
    ok "PostgREST placeholder schema exists"
  else
    warn "PostgREST schema missing — run migration 003"
  fi
fi

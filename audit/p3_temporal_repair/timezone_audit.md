# Timezone audit

The reconstructed Ireland input and historical artifacts parse as
timezone-naive wall-clock timestamps, and no
authoritative UTC/local declaration is persisted. Madrid and Ireland both
observe DST, so naive timestamps cannot safely establish elapsed real hours
across transitions.

The repair performs timestamp arithmetic rather than assuming 24 rows per civil
day, rejects duplicates, and includes an aware-DST elapsed-time test. Production
regeneration remains gated until each restored input is explicitly declared as
UTC or localized with documented ambiguous/nonexistent-time handling.

Madrid remains `TIMEZONE_CONTRACT_UNVERIFIABLE`; Ireland is explicitly treated
as naive source time with exact timestamp equality, without assuming 24 rows per
civil day.

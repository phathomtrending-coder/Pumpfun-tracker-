alter table tracked_tokens
add column if not exists status text default 'watchlist',
add column if not exists posted_to_watchlist boolean default false,
add column if not exists posted_to_public boolean default false,
add column if not exists trend_score integer default 0,
add column if not exists safety_score integer default 0,
add column if not exists dev_score integer default 50,
add column if not exists rug_dna_score integer default 50,
add column if not exists risk_flags jsonb default '[]'::jsonb;

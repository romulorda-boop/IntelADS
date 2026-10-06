-- Eventos de aparição usados para estimar frequência nos 30 dias anteriores.
-- is_mock distingue as linhas de seed dos futuros eventos capturados.
CREATE TABLE IF NOT EXISTS ad_appearances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_id UUID NOT NULL REFERENCES ads(id) ON DELETE CASCADE,
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_mock BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_ad_appearances_ad_observed
    ON ad_appearances (ad_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_ad_appearances_observed
    ON ad_appearances (observed_at DESC);

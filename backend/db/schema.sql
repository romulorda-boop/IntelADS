-- Tabela de Anunciantes / Empresas

CREATE TABLE advertisers (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,

    domain VARCHAR(255),

    facebook_page_id VARCHAR(100),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- Tabela de Aplicativos Vinculados

CREATE TABLE apps (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    advertiser_id UUID REFERENCES advertisers(id) ON DELETE CASCADE,

    platform VARCHAR(20) NOT NULL, -- 'android' ou 'ios'

    store_app_id VARCHAR(255) NOT NULL, -- package_name ou track_id

    title VARCHAR(255) NOT NULL,

    icon_url TEXT,

    downloads_count VARCHAR(50), -- Ex: '100.000.000+'

    rating NUMERIC(3, 2),

    category VARCHAR(100),

    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_app_platform UNIQUE (platform, store_app_id)

);

-- Tabela Principal de Anúncios

CREATE TABLE ads (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    advertiser_id UUID REFERENCES advertisers(id) ON DELETE SET NULL,

    app_id UUID REFERENCES apps(id) ON DELETE SET NULL,

    title TEXT,

    caption_text TEXT,

    media_type VARCHAR(20) NOT NULL, -- 'video', 'image', 'carrousel'

    media_url TEXT NOT NULL,

    thumbnail_url TEXT NOT NULL,

    source_network VARCHAR(30) NOT NULL, -- 'meta', 'google', 'tiktok', 'kwai'

    category VARCHAR(50) NOT NULL, -- 'games', 'ecommerce', 'apps', 'finance', 'infoproducts'

    target_os VARCHAR(20)[] NOT NULL, -- ARRAY ['android', 'ios', 'desktop']

    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,

    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    longevity_score INT DEFAULT 0,

    phash VARCHAR(64),

    destination_url TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- Tabela de Relação para Criativos Similares (pHash)

CREATE TABLE ad_variations (

    parent_ad_id UUID REFERENCES ads(id) ON DELETE CASCADE,

    variation_ad_id UUID REFERENCES ads(id) ON DELETE CASCADE,

    hamming_distance INT NOT NULL,

    PRIMARY KEY (parent_ad_id, variation_ad_id)

);

-- Índices de Performance

CREATE INDEX idx_ads_longevity ON ads(longevity_score DESC);

CREATE INDEX idx_ads_network_category ON ads(source_network, category);

CREATE INDEX idx_ads_phash ON ads(phash);

CREATE INDEX idx_apps_store_id ON apps(store_app_id);

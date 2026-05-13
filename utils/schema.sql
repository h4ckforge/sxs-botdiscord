-- ============================================================
-- SxS Bot — Creación de tablas
-- ============================================================

-- TEMPORADAS
CREATE TABLE temporadas (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    activa BOOLEAN DEFAULT FALSE
);

-- MIEMBROS
CREATE TABLE miembros (
    id SERIAL PRIMARY KEY,
    discord_user_id TEXT UNIQUE NOT NULL,
    nombre TEXT,
    avatar TEXT,
    ign_pc TEXT,
    ign_ps TEXT,
    ign_xbox TEXT,
    ign_resurgence TEXT,
    clan_pc TEXT,
    clan_ps TEXT,
    clan_xbox TEXT,
    clan_resurgence TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    is_moderador BOOLEAN DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT NOW()
);

-- XP TEMPORADA
CREATE TABLE xp_temporada (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER REFERENCES miembros(id) ON DELETE CASCADE,
    temporada_id INTEGER REFERENCES temporadas(id) ON DELETE CASCADE,
    xp_eventos INTEGER DEFAULT 0,
    xp_chat INTEGER DEFAULT 0,
    xp_voz INTEGER DEFAULT 0,
    xp_total INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    eventos_creados INTEGER DEFAULT 0,
    eventos_participados INTEGER DEFAULT 0,
    UNIQUE(miembro_id, temporada_id)
);

-- XP SHEPHERD
CREATE TABLE xp_shepherd (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER REFERENCES miembros(id) ON DELETE CASCADE UNIQUE,
    xp_shepherd INTEGER DEFAULT 0,
    raids_participadas INTEGER DEFAULT 0,
    raids_creadas INTEGER DEFAULT 0
);

-- ACTIVIDADES
CREATE TABLE actividades (
    id SERIAL PRIMARY KEY,
    juego TEXT NOT NULL,
    nombre TEXT NOT NULL,
    is_raid BOOLEAN DEFAULT FALSE,
    xp_base INTEGER DEFAULT 10,
    xp_bonus_creador INTEGER DEFAULT 2,
    min_participantes INTEGER DEFAULT 1,
    max_participantes INTEGER DEFAULT 8,
    max_reservas INTEGER DEFAULT 2
);

-- EVENTOS
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    actividad_id INTEGER REFERENCES actividades(id),
    creador_id INTEGER REFERENCES miembros(id),
    temporada_id INTEGER REFERENCES temporadas(id),
    confirmado_por INTEGER REFERENCES miembros(id),
    guild_id TEXT,
    channel_id TEXT,
    message_id TEXT,
    fecha_evento TIMESTAMP,
    estado TEXT DEFAULT 'abierto',
    xp_total_concedido INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- PARTICIPANTES EVENTO
CREATE TABLE participantes_evento (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    miembro_id INTEGER REFERENCES miembros(id) ON DELETE CASCADE,
    es_reserva BOOLEAN DEFAULT FALSE,
    xp_ganado INTEGER DEFAULT 0,
    confirmado BOOLEAN DEFAULT FALSE,
    UNIQUE(evento_id, miembro_id)
);

-- LISTA DE ESPERA
CREATE TABLE lista_espera (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER REFERENCES miembros(id) ON DELETE CASCADE,
    actividad_id INTEGER REFERENCES actividades(id) ON DELETE CASCADE,
    posicion INTEGER,
    fecha_inscripcion TIMESTAMP DEFAULT NOW(),
    recibio_item BOOLEAN DEFAULT FALSE,
    fecha_recepcion TIMESTAMP,
    UNIQUE(miembro_id, actividad_id)
);

-- XP CHAT LOG
CREATE TABLE xp_chat_log (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER REFERENCES miembros(id) ON DELETE CASCADE,
    guild_id TEXT,
    channel_id TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    xp_ganado INTEGER DEFAULT 0
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX idx_miembros_discord_user_id ON miembros(discord_user_id);
CREATE INDEX idx_xp_temporada_temporada_id ON xp_temporada(temporada_id);
CREATE INDEX idx_xp_temporada_miembro_id ON xp_temporada(miembro_id);
CREATE INDEX idx_eventos_temporada_id ON eventos(temporada_id);
CREATE INDEX idx_participantes_evento_id ON participantes_evento(evento_id);
CREATE INDEX idx_xp_chat_log_miembro_id ON xp_chat_log(miembro_id);

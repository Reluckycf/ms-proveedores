-- ms-proveedores (PRV) - Inicialización PostgreSQL (psql)
-- Crea la base de datos y las tablas requeridas.

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', 'proveedores', 'proveedores123')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'proveedores')\gexec

SELECT format('CREATE DATABASE %I OWNER %I', 'ms_proveedores', 'proveedores')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ms_proveedores')\gexec

ALTER DATABASE ms_proveedores OWNER TO proveedores;
GRANT ALL PRIVILEGES ON DATABASE ms_proveedores TO proveedores;

\connect ms_proveedores

GRANT CREATE ON SCHEMA public TO proveedores;
SET ROLE proveedores;

CREATE TABLE IF NOT EXISTS proveedores (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  nit VARCHAR(20) NOT NULL UNIQUE,
  razon_social VARCHAR(255) NOT NULL,
  nombre_contacto VARCHAR(255) NOT NULL,
  email VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  direccion VARCHAR(255) NOT NULL,
  ciudad VARCHAR(100) NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'activo',
  fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE,
  puntaje_evaluacion DOUBLE PRECISION NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS contratos (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  proveedor_id INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
  numero_contrato VARCHAR(50) NOT NULL UNIQUE,
  objeto_contrato TEXT NOT NULL,
  monto_total NUMERIC(15,2) NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  estado VARCHAR(30) NOT NULL DEFAULT 'vigente',
  url_documento TEXT NULL,
  observaciones TEXT NULL
);

CREATE INDEX IF NOT EXISTS ix_contratos_proveedor_id ON contratos (proveedor_id);
CREATE INDEX IF NOT EXISTS ix_contratos_estado_fecha_fin ON contratos (estado, fecha_fin);

CREATE TABLE IF NOT EXISTS evaluaciones (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  proveedor_id INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
  contrato_id INTEGER NOT NULL REFERENCES contratos(id) ON DELETE CASCADE,
  periodo_evaluacion VARCHAR(50) NOT NULL,
  calidad INTEGER NOT NULL,
  cumplimiento_tiempos INTEGER NOT NULL,
  precio_competitivo INTEGER NOT NULL,
  servicio_postventa INTEGER NOT NULL,
  puntaje_total DOUBLE PRECISION NOT NULL,
  evaluador_id VARCHAR(100) NOT NULL,
  fecha_evaluacion DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX IF NOT EXISTS ix_evaluaciones_proveedor_id ON evaluaciones (proveedor_id);
CREATE INDEX IF NOT EXISTS ix_evaluaciones_contrato_id ON evaluaciones (contrato_id);

CREATE TABLE IF NOT EXISTS cotizaciones (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  proveedor_id INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
  descripcion TEXT NOT NULL,
  precio_unitario NUMERIC(15,2) NOT NULL,
  condiciones_comerciales TEXT NULL,
  vigencia_cotizacion DATE NOT NULL,
  fecha_cotizacion DATE NOT NULL DEFAULT CURRENT_DATE,
  estado VARCHAR(20) NOT NULL DEFAULT 'activa'
);

CREATE INDEX IF NOT EXISTS ix_cotizaciones_proveedor_id ON cotizaciones (proveedor_id);

CREATE TABLE IF NOT EXISTS documentos_proveedor (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  proveedor_id INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
  tipo_documento VARCHAR(30) NOT NULL,
  nombre_documento VARCHAR(255) NOT NULL,
  url_archivo TEXT NOT NULL,
  fecha_emision DATE NOT NULL,
  fecha_vencimiento DATE NOT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'vigente',
  fecha_carga TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_documentos_proveedor_proveedor_id ON documentos_proveedor (proveedor_id);
CREATE INDEX IF NOT EXISTS ix_documentos_proveedor_estado_fecha_vencimiento ON documentos_proveedor (estado, fecha_vencimiento);

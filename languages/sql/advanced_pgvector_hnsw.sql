-- SQL / pgvector — Advanced Example: Tenant-Isolated Evidence Vector Store
--
-- What: A durable embedding index with HNSW search, tenant isolation, immutable
-- content fingerprints, idempotent identity, and a bounded search function.
-- Where: Evidence retrieval, agent memory, semantic case search, and knowledge services.
-- When: Vector similarity must coexist with relational constraints and access policy.
-- Why: PostgreSQL centralizes transactions, RLS, indexes, and set-oriented correctness.
-- How: pgvector cosine HNSW, row-level security, constrained metadata, deterministic
-- identity fields, and SECURITY INVOKER search preserve the database trust boundary.

BEGIN;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS evidence_embedding (
  tenant_id uuid NOT NULL,
  artifact_id uuid NOT NULL,
  chunk_index integer NOT NULL CHECK (chunk_index >= 0),
  content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
  embedding vector(1536) NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  PRIMARY KEY (tenant_id, artifact_id, chunk_index),
  UNIQUE (tenant_id, content_sha256, chunk_index)
);

CREATE INDEX IF NOT EXISTS evidence_embedding_hnsw_cosine
  ON evidence_embedding USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 96);

CREATE INDEX IF NOT EXISTS evidence_embedding_metadata_gin
  ON evidence_embedding USING gin (metadata jsonb_path_ops);

ALTER TABLE evidence_embedding ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON evidence_embedding;
CREATE POLICY tenant_isolation ON evidence_embedding
  USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);

CREATE OR REPLACE FUNCTION search_evidence(
  p_tenant_id uuid,
  p_query vector(1536),
  p_limit integer DEFAULT 10,
  p_max_cosine_distance real DEFAULT 0.35
)
RETURNS TABLE (
  artifact_id uuid,
  chunk_index integer,
  content_sha256 text,
  cosine_distance real,
  metadata jsonb
)
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
BEGIN
  IF p_limit < 1 OR p_limit > 100 THEN
    RAISE EXCEPTION 'p_limit must be between 1 and 100';
  END IF;
  IF p_max_cosine_distance < 0 OR p_max_cosine_distance > 2 THEN
    RAISE EXCEPTION 'cosine distance must be between 0 and 2';
  END IF;
  PERFORM set_config('hnsw.ef_search', greatest(40, p_limit * 4)::text, true);
  RETURN QUERY
    SELECT e.artifact_id,
           e.chunk_index,
           e.content_sha256,
           (e.embedding <=> p_query)::real,
           e.metadata
      FROM evidence_embedding AS e
     WHERE e.tenant_id = p_tenant_id
       AND (e.embedding <=> p_query) <= p_max_cosine_distance
     ORDER BY e.embedding <=> p_query, e.artifact_id, e.chunk_index
     LIMIT p_limit;
END;
$$;

COMMENT ON FUNCTION search_evidence(uuid, vector, integer, real) IS
  'Tenant-scoped HNSW cosine retrieval with bounded result count and explicit distance threshold.';
COMMIT;

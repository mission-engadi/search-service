"""Initial search service migration

Revision ID: 001
Revises: 
Create Date: 2024-12-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create search_indexes table
    op.create_table(
        'search_indexes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_type', sa.Enum(
            'article', 'story', 'partner', 'project', 'social_post', 'notification', 'campaign',
            name='documenttype'
        ), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('indexed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for search_indexes
    op.create_index('idx_search_vector', 'search_indexes', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index('idx_document_id', 'search_indexes', ['document_id'], unique=False)
    op.create_index('idx_document_type', 'search_indexes', ['document_type'], unique=False)
    op.create_index('idx_language', 'search_indexes', ['language'], unique=False)
    op.create_index('idx_document_type_language', 'search_indexes', ['document_type', 'language'], unique=False)
    op.create_index('idx_published_at', 'search_indexes', ['published_at'], unique=False)
    op.create_index('idx_author_id', 'search_indexes', ['author_id'], unique=False)
    op.create_index('idx_metadata', 'search_indexes', ['metadata'], unique=False, postgresql_using='gin')
    
    # Create trigger to automatically update search_vector
    op.execute("""
        CREATE FUNCTION search_indexes_trigger() RETURNS trigger AS $$
        begin
          new.search_vector :=
            setweight(to_tsvector(COALESCE(new.language, 'english')::regconfig, COALESCE(new.title, '')), 'A') ||
            setweight(to_tsvector(COALESCE(new.language, 'english')::regconfig, COALESCE(new.content, '')), 'B') ||
            setweight(to_tsvector(COALESCE(new.language, 'english')::regconfig, COALESCE(new.author_name, '')), 'C');
          return new;
        end
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON search_indexes FOR EACH ROW EXECUTE FUNCTION search_indexes_trigger();
    """)
    
    # Create search_queries table
    op.create_table(
        'search_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('query_text', sa.String(length=500), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('results_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('clicked_result_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for search_queries
    op.create_index('idx_query_text', 'search_queries', ['query_text'], unique=False)
    op.create_index('idx_user_id', 'search_queries', ['user_id'], unique=False)
    op.create_index('idx_created_at', 'search_queries', ['created_at'], unique=False)
    op.create_index('idx_query_text_created', 'search_queries', ['query_text', 'created_at'], unique=False)
    op.create_index('idx_user_created', 'search_queries', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_results_count', 'search_queries', ['results_count'], unique=False)
    
    # Create search_suggestions table
    op.create_table(
        'search_suggestions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('suggestion_text', sa.String(length=200), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('suggestion_text')
    )
    
    # Create indexes for search_suggestions
    op.create_index('idx_suggestion_text', 'search_suggestions', ['suggestion_text'], unique=False)
    op.create_index('idx_suggestion_language', 'search_suggestions', ['language'], unique=False)
    op.create_index('idx_suggestion_usage', 'search_suggestions', ['usage_count', 'last_used_at'], unique=False)
    op.create_index('idx_suggestion_language_usage', 'search_suggestions', ['language', 'usage_count'], unique=False)
    
    # Create index_jobs table
    op.create_table(
        'index_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.Enum(
            'full_reindex', 'incremental', 'single_document', 'bulk',
            name='jobtype'
        ), nullable=False),
        sa.Column('status', sa.Enum(
            'pending', 'running', 'completed', 'failed',
            name='jobstatus'
        ), nullable=False, server_default='pending'),
        sa.Column('source_service', sa.String(length=100), nullable=True),
        sa.Column('documents_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('documents_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for index_jobs
    op.create_index('idx_job_status', 'index_jobs', ['status'], unique=False)
    op.create_index('idx_job_created', 'index_jobs', ['created_at'], unique=False)
    op.create_index('idx_job_status_created', 'index_jobs', ['status', 'created_at'], unique=False)
    op.create_index('idx_job_type_status', 'index_jobs', ['job_type', 'status'], unique=False)
    
    # Install pg_trgm extension for fuzzy search/autocomplete
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # Create trigram index for autocomplete
    op.create_index(
        'idx_suggestion_text_trgm',
        'search_suggestions',
        ['suggestion_text'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'suggestion_text': 'gin_trgm_ops'}
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('index_jobs')
    op.drop_table('search_suggestions')
    op.drop_table('search_queries')
    
    # Drop trigger and function for search_indexes
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON search_indexes;")
    op.execute("DROP FUNCTION IF EXISTS search_indexes_trigger();")
    
    op.drop_table('search_indexes')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS jobstatus;")
    op.execute("DROP TYPE IF EXISTS jobtype;")
    op.execute("DROP TYPE IF EXISTS documenttype;")
    
    # Drop extension
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")

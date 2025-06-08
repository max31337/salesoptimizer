from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from typing import Any, Literal
# Add your project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))  # alembic folder
db_dir = os.path.dirname(current_dir)  # db folder
infra_dir = os.path.dirname(db_dir)  # infrastructure folder
project_root = os.path.dirname(infra_dir)  # project root
sys.path.insert(0, project_root)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and models AFTER adding to sys.path
try:
    from infrastructure.db.database import Base, get_database_url
    # Import ALL model files here to register them with SQLAlchemy
    from infrastructure.db.models.user_model import UserModel, GUID  # Add GUID import
    from infrastructure.db.models.tenant_model import TenantModel
    from infrastructure.db.models.team_model import TeamModel
    from infrastructure.db.models.invitation_model import InvitationModel
    from infrastructure.db.models.refresh_token_model import RefreshTokenModel
    from infrastructure.db.models.profile_update_request_model import ProfileUpdateRequestModel
    from infrastructure.db.models.activity_log_model import ActivityLogModel

    # Reference models to avoid "import not accessed" warning
    _models: list[type] = [UserModel, TenantModel, TeamModel, InvitationModel, RefreshTokenModel, ProfileUpdateRequestModel, ActivityLogModel]

    print(f"✅ Successfully imported Base and models")
    print(f"📋 Registered tables: {list(Base.metadata.tables.keys())}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    raise

# Set the SQLAlchemy URL
def get_url():
    try:
        url = get_database_url()
        print(f"🔗 Using database URL: {url}")
        return url
    except Exception as e:
        print(f"Error getting database URL: {e}")
        return "postgresql://postgres@localhost:5432/salesoptimizer_db"

config.set_main_option("sqlalchemy.url", get_url())

target_metadata = Base.metadata


def render_item(
    type_: str,
    obj: Any,
    autogen_context: Any
) -> str | Literal[False]:
    """Render custom types properly in migrations."""
    if type_ == "type" and isinstance(obj, GUID):
        # Add the import to the migration file
        autogen_context.imports.add("from infrastructure.db.models.user_model import GUID")
        return "GUID()"
    
    # Return False for default rendering
    return False

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        render_item=render_item,  
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            render_item=render_item, 
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

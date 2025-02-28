from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importar modelos para que Alembic los detecte
from app.db.base import Base
from app.models.user import User
from app.models.profile import Profile
from app.core.config import settings

# Acceso a la configuración de alembic.ini
config = context.config

# Interpretación del archivo de configuración de logging si existe
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Establecer el 'target_metadata' con el objeto 'Base.metadata' importado de los modelos
target_metadata = Base.metadata

# Sobrescribir el valor de sqlalchemy.url en alembic.ini con nuestra URL de base de datos
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI_VALUE)

def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'.
    
    Esto configura el contexto con solo una URL y no un Engine,
    aunque en la práctica Engine no se usa en el contexto 'offline'.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecutar migraciones en modo 'online'.
    
    En este escenario tenemos acceso a un Engine y podemos usar begin_transaction()
    directamente, o usar run_migrations().
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
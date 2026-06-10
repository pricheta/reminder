from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import String, Integer, DateTime, create_engine, select, update, Boolean, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    next_time_to_do: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class DatabaseClientConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    HOST: str
    PORT: int
    DB: str
    USER: str
    PASSWORD: str

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


class DatabaseClient:
    def __init__(self, config: DatabaseClientConfig):
        self.config = config
        self.engine = create_engine(
            self.config.database_url,
            echo=False,
        )
        self.session_maker = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False
        )

    def get_task(self, task_id: int) -> Task | None:
        with self.session_maker() as session:
            statement = select(Task).where(Task.id == task_id)
            return session.scalars(statement).first()

    def get_all_tasks(self) -> list[Task]:
        with self.session_maker() as session:
            statement = select(Task)
            return list(session.scalars(statement))

    def update_task_next_time_to_do(self, task_id: int, next_time_to_do: datetime):
        with self.session_maker() as session:
            statement = (
                update(Task)
                .where(Task.id == task_id)
                .values(next_time_to_do=next_time_to_do)
            )
            session.execute(statement)
            session.commit()

    def delete_task(self, task_id: int) -> None:
        with self.session_maker() as session:
            statement = delete(Task).where(Task.id == task_id)
            session.execute(statement)
            session.commit()

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import String, Integer, DateTime, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    frequency_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    last_time_done: Mapped[datetime] = mapped_column(DateTime, nullable=False)


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

    def update_task_last_time_done(self, task_title: str, last_time_done: datetime):
        with self.session_maker() as session:
            task = session.query(Task).filter(Task.title == task_title).first()
            task.last_time_done = last_time_done
            session.commit()

    def get_all_tasks(self) -> list[Task]:
        with self.session_maker() as session:
            return list(session.scalars(select(Task)))

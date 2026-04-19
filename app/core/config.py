from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "PGR Mastering"
    max_upload_mb: int = 300
    data_dir: str = "/data"
    upload_dir: str = "/data/uploads"
    output_dir: str = "/data/outputs"
    jobs_dir: str = "/data/jobs"
    learning_dir: str = "/data/learning"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    analysis_max_seconds: int = 60
    process_max_seconds: int = 420
    target_sr: int = 44100
    enable_free_plugin_hooks: int = 0
    ladspa_plugin_spec: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

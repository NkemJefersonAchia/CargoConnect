import importlib


def reload_config_module():
    import config.config as config_module

    return importlib.reload(config_module)


def test_config_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)

    config_module = reload_config_module()
    cfg = config_module.Config

    assert cfg.SECRET_KEY == "dev-secret-key-change-in-production"
    assert cfg.SQLALCHEMY_DATABASE_URI == "postgresql://postgres:password@localhost:5432/cargoconnect"
    assert cfg.DEBUG is True


def test_config_reads_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "unit-test-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///unit_test.db")
    monkeypatch.setenv("FLASK_DEBUG", "0")

    config_module = reload_config_module()
    cfg = config_module.Config

    assert cfg.SECRET_KEY == "unit-test-key"
    assert cfg.SQLALCHEMY_DATABASE_URI == "sqlite:///unit_test.db"
    assert cfg.DEBUG is False

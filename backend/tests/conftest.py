"""
Pytest configuration and shared fixtures.
"""

import os
import tempfile

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base


# ==========================================================
# TEST DATABASE CONFIG
# ==========================================================

TEST_DB_FILE = os.path.join(
    tempfile.gettempdir(),
    "automated_test_generator_test.db"
)

SQLALCHEMY_TEST_DATABASE_URL = (
    f"sqlite:///{TEST_DB_FILE}"
)


# ==========================================================
# ENGINE
# ==========================================================

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    echo=False
)


# ==========================================================
# SESSION FACTORY
# ==========================================================

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================================
# CREATE TEST TABLES
# ==========================================================

Base.metadata.create_all(
    bind=engine
)


# ==========================================================
# DATABASE FIXTURE
# ==========================================================

@pytest.fixture(scope="function")
def db():
    """
    Creates a fresh database session
    for every test.
    """

    connection = engine.connect()

    transaction = connection.begin()

    session = TestingSessionLocal(
        bind=connection
    )

    try:

        yield session

    finally:

        session.close()

        transaction.rollback()

        connection.close()


# ==========================================================
# TEMP DIRECTORY FIXTURE
# ==========================================================

@pytest.fixture(scope="function")
def temp_dir():
    """
    Creates temporary directory
    for file-based tests.
    """

    with tempfile.TemporaryDirectory() as tmpdir:

        yield tmpdir


# ==========================================================
# SAMPLE PYTHON FILE FIXTURE
# ==========================================================

@pytest.fixture(scope="function")
def sample_python_file(temp_dir):

    file_path = os.path.join(
        temp_dir,
        "sample.py"
    )

    code = """
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:

    def multiply(self, a, b):
        return a * b
"""

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(code)

    return file_path


# ==========================================================
# SAMPLE JS FILE FIXTURE
# ==========================================================

@pytest.fixture(scope="function")
def sample_js_file(temp_dir):

    file_path = os.path.join(
        temp_dir,
        "sample.js"
    )

    code = """
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => {
    return a - b;
};

class Calculator {
    multiply(a, b) {
        return a * b;
    }
}
"""

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(code)

    return file_path


# ==========================================================
# CLEANUP
# ==========================================================

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():

    yield

    try:

        if os.path.exists(TEST_DB_FILE):

            os.remove(TEST_DB_FILE)

    except Exception:
        pass
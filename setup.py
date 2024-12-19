from setuptools import setup, find_packages

setup(
    name="factupicer",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'fastapi',
        'python-jose[cryptography]',
        'passlib',
        'python-multipart',
        'python-dotenv',
        'reportlab',
        'alembic',
        'pytz',
        'uvicorn'
    ],
) 
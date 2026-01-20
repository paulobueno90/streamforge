from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Real-time cryptocurrency data ingestion system"

setup(
    name='streamforge',
    version='0.1.1',
    description='Real-time cryptocurrency data ingestion system',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Paulo Bueno',
    author_email='paulohmbueno@gmail.com',
    url='https://github.com/paulobueno90/streamforge',
    packages=find_packages(exclude=['tests*', 'docs*']),
    package_data={
        'streamforge': ['*.py'],
    },
    include_package_data=True,
    install_requires=[
        'aiohttp>=3.8.0',
        'websockets>=10.0',
        'sqlalchemy>=1.4.0',
        'pandas>=1.3.0',
        'pydantic>=1.8.0',
        'orjson>=3.6.0',
        'aiokafka>=0.8.0',
        'asyncpg>=0.27.0',
        'aiolimiter>=1.1.0',
        'python-dateutil>=2.8.0',
        'numpy>=1.20.0',
        'requests>=2.25.0',
        'ciso8601>=2.2.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.18.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial',
    ],
    keywords='cryptocurrency, stocks, options, trading, data, ingestion, websocket, binance, kraken, okx, streamforge',
    # entry_points={
    #     'console_scripts': [
    #         'streamforge=streamforge.cli:main',
    #     ],
    # },
)
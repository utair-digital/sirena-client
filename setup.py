import setuptools

with open("README.md", "r", encoding='utf-8') as readme:
    long_description = readme.read()

install_requires = ['xmltodict~=0.12.0', 'pycryptodome==3.10.1', 'pydantic', ]

async_require = ['aioredis==1.3.1', 'asyncio~=3.4.3', 'aiofile~=3.7.2']
sync_require = ['redis==4.0.2', ]

setuptools.setup(
    name="sirena_client",
    version="0.0.10",
    python_requires='>=3.8',
    author="Utair Digital",
    description="Sirena Travel Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/utair-digital/sirena-client",
    install_requires=install_requires,
    keywords=['sirena', 'client'],
    license="Apache License Version 2.0",
    extras_require={
        'async': async_require,
        'sync': sync_require,
    },
    packages=setuptools.find_packages(exclude=('examples', 'tests', )),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "License :: Apache License Version 2.0",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
)

import setuptools

setuptools.setup(
    name='tbzuploader',
    version='2017.9.0',
    license='Apache Software License 2.0',
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=[
        'requests',
        'future',
    ],

    include_package_data=True,

    entry_points={
        'console_scripts': [
            'tbzuploader=tbzuploader.console_scripts:main',
        ],
    }
)

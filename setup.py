import setuptools

setuptools.setup(
    name='tbzuploader',
    version='2017.1',
    license='Apache Software License 2.0',
    long_description=open('README.txt').read(),
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=[
        'requests',
    ],

    include_package_data=True,

    entry_points={
        'console_scripts': [
            'tbzuploader=tbzuploader.console_scripts:main',
        ],
    }
)

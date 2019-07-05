import setuptools

setuptools.setup(
    name='tbzuploader',
    version='2019.12.0',
    license='Apache Software License 2.0',
    long_description=open('README.rst').read(),
    url='https://github.com/tbz-pariv/tbzuploader',
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=[
        'requests',
        'future',
    ],

    include_package_data=True,

    author='TBZ-PARIV GmbH',
    author_email='info@tbz-pariv.de',

    entry_points={
        'console_scripts': [
            'tbzuploader=tbzuploader.console_scripts:main',
        ],
    }
)

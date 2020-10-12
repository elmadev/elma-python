from setuptools import setup


setup(
    name='elma',
    version='0.8.0',
    url='http://github.com/sigvef/elma/',
    license='MIT',
    maintainer='Sigve Sebastian Farstad',
    maintainer_email='sigvefarstad@gmail.com',
    description='Elma Python Library.',
    test_suite="tests",
    packages=['elma'],
    install_requires=[
        'pillow>=4.0.0',
    ],
    tests_require=[
        'flake8>=3.3.0',
        'mypy>=0.700'
    ]
)

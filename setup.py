from setuptools import setup


setup(
    name='elma',
    version='0.7',
    url='http://github.com/sigvef/elma/',
    license='MIT',
    maintainer='Sigve Sebastian Farstad',
    maintainer_email='sigvefarstad@gmail.com',
    description='Elma Python Library.',
    test_suite="tests",
    packages=['elma'],
    install_requires=[
        'pillow==4.0.0',
    ],
)

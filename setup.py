from setuptools import find_packages, setup


setup(
    name='acmclient',
    version="0.1",
    url='https://github.com/yangjiaronga/acmclient/',
    license='MIT',
    author='yangjiaronga',
    author_email='yangjiaronga@gmail.com',
    description='Aliyun acm client for Python',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
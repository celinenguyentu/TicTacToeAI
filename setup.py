from setuptools import setup, find_packages

setup(
    name='TicTacToeAI',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pillow',
    ],
    author='Céline Nguyen',
    author_email='celine.nguyentu@gmail.com',
    description='An AI built by adversarial reinforcement learning for Tic Tac Toe.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/celinenguyentu/TicTacToeAI',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)

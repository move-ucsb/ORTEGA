from setuptools import setup

if __name__ == "__main__":
    setup(
        name='ortega',
        version='1.0.12',
        author='MOVE lab@UCSB',
        author_email="rongxiangsu@ucsb.edu",
        packages=["ortega"],
        url='https://github.com/move-ucsb/ORTEGA',
        license='MIT',
        description='ORTEGA',
        install_requires=[
            "numpy",
            "pandas",
            "shapely",
            "attrs",
            "matplotlib",
            "typing_extensions",
        ],
    )

from setuptools import setup

if __name__ == "__main__":
    setup(
        name='ortega',
        version='0.0.34',
        author='MOVE lab@UCSB',
        author_email="rongxiangsu@ucsb.edu",
        packages=["ortega"],
        url='https://move.geog.ucsb.edu/',
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

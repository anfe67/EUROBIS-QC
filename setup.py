from setuptools import setup, find_packages

setup(name="eurobisqc",
      version="0.1.0",
      python_requires='>=3.6',
      url="https://github.com/anfe67/eurobis-qc",
      license="MIT",
      author="Antonio Ferraro",
      author_email="antonio.ferraro@safits.be",
      description="EUROBIS QC checks",
      packages=find_packages(),
      zip_safe=False)

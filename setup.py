from setuptools import setup, find_packages

# The database contains the big part of WORMS and it is BIG - not sure whether I want to distribute it.

setup(name="eurobisqc",
      version="0.2.0",
      python_requires='>=3.6',
      data_files=[  # ('database', ['lookupdb/database/EUROBIS_QC_LOOKUP_DB.tar.gz']),
          ('resources', ['lookupdb/resources/config.ini',
                         'lookupdb/resources/countMeasurementTypeIDLookup',
                         'lookupdb/resources/countMeasurementTypeLookup',
                         'lookupdb/resources/sampleSizeMeasurementTypeIDLookup',
                         'lookupdb/resources/sampleSizeMeasurementTypeLookup',
                         'lookupdb/resources/weightMeasurementTypeIDLookup',
                         'lookupdb/resources/weightMeasurementTypeIDLookup',
                         'lookupdb/resources/README.md']),
          ('docs', ['lookupdb/IMPORT_WORMS.md',
                    'lookupdb/README.md',
                    'lookupdb/csvkit-readthedocs-io-en-latest.pdf',
                    'eurobisqc/DEV_NOTES.md',
                    'eurobisqc/test/README.md',
                    ])
      ],
      url="https://github.com/anfe67/eurobis-qc",
      license="MIT",
      author="Antonio Ferraro",
      author_email="antonio.ferraro@safits.be",
      description="EUROBIS QC checks",
      py_modules=['eurobisqc', 'lookupdb'],
      packages=find_packages(),
      tests_require=['nose>=1.0', 'coverage'],
      zip_safe=False)

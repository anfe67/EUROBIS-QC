from setuptools import setup, find_packages

# The database contains a big part of WORMS and it is BIG - not sure whether I want to distribute it.

setup(name="eurobisqc",
      version="0.3.0",
      python_requires='>=3.6',
      data_files=[  # ('database', ['dbworks/database/EUROBIS_QC_LOOKUP_DB.tar.gz']),
          ('resources', ['dbworks/resources/config.ini',
                         'dbworks/resources/countMeasurementTypeIDLookup',
                         'dbworks/resources/countMeasurementTypeLookup',
                         'dbworks/resources/sampleSizeMeasurementTypeIDLookup',
                         'dbworks/resources/sampleSizeMeasurementTypeLookup',
                         'dbworks/resources/weightMeasurementTypeIDLookup',
                         'dbworks/resources/weightMeasurementTypeIDLookup',
                         'dbworks/resources/VERIFICATIONS.md']),
          ('docs', ['dbworks/IMPORT_WORMS.md',
                    'dbworks/VERIFICATIONS.md',
                    'dbworks/csvkit-readthedocs-io-en-latest.pdf',
                    'eurobisqc/DEV_NOTES.md',
                    'eurobisqc/test/VERIFICATIONS.md',
                    ])
      ],
      url="https://github.com/anfe67/eurobis-qc",
      license="MIT",
      author="Antonio Ferraro",
      author_email="antonio.ferraro@safits.be",
      description="EUROBIS QC checks",
      py_modules=['eurobisqc', 'dbworks'],
      packages=find_packages(),
      tests_require=['nose>=1.0', 'coverage'],
      zip_safe=False)

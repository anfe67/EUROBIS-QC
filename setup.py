import os
from setuptools import setup, find_packages

# The database contains a big part of WORMS and it is BIG - not sure whether I want to distribute it.
# In any case need to cope with it

setup(name="eurobisqc",
      version="0.4.0",
      python_requires='>=3.6',
      data_files=[('dbworks/database', ['EUROBIS_QC_LOOKUP_DB.db']),
                  ('dbworks/resources', ['dbworks/resources/config.ini',
                                         'dbworks/resources/countMeasurementTypeIDLookup',
                                         'dbworks/resources/countMeasurementTypeLookup',
                                         'dbworks/resources/sampleSizeMeasurementTypeIDLookup',
                                         'dbworks/resources/sampleSizeMeasurementTypeLookup',
                                         'dbworks/resources/weightMeasurementTypeIDLookup',
                                         'dbworks/resources/weightMeasurementTypeIDLookup',
                                         'dbworks/resources/basisOfRecordValuesLookup',
                                         'dbworks/resources/recommendedFieldsLookUP',
                                         'dbworks/resources/requiredFieldsLookUP',
                                         'dbworks/resources/sexMeasurementTypeIDLookup',
                                         'dbworks/resources/sexMeasurementTypeLookup',
                                         'dbworks/resources/sexValuesLookup'
                                         ]),
                  ('docs', ['dbworks/IMPORT_WORMS.md',
                            'dbworks/README_DBWORKS.md',
                            'dbworks/csvkit-readthedocs-io-en-latest.pdf',
                            'dbworks/resources/README_RESOURCES.md',
                            'DEV_NOTES.md',
                            'README.md',
                            'eurobisqc/test/VERIFICATIONS.md',
                            'eurobisqc/README_EUROBISQC.md',
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

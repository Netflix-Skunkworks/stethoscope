Practices
=========

.. warning:: Stethoscope's handling of practices is currently undergoing a review and
   rearchitecture; as such, the content of this document should be considered subject to
   change and the APIs highly unstable.

Practices are configured in the same file as the API server (see :ref:`backend-configuration`). The
file should have a top-level ``PRACTICES`` dictionary in which each key is the name [#entrypoint]_
of a practice and the value is the configuration dictionary for that practice. For an example file,
see the defaults in :file:`stethoscope/api/defaults.py`.

.. [#entrypoint] The name referred to here is the *entry point name* within the
   ``stethoscope.plugins.practices.devices`` namespace. The default entry points are defined in
   :file:`setup.py`. Additional entry points can be defined in your own packages and registered via
   :py:mod:`setuptools` (see `Dynamic Discovery of Services and Plugins`_). All of the entry points
   registered in the ``stethoscope.plugins.practices.devices`` namespace are available for use, but
   only those configured in the ``PRACTICES`` dictionary will actually be used by Stethoscope.

.. _Dynamic Discovery of Services and Plugins:
  http://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins


Default Practice Types
----------------------

Stethoscope defines classes which are used to derive practices via registered entry points. These
classes are defined in :file:`stethoscope/plugins/practices.py`, the entry points registered in
:file:`setup.py`, and example configurations available in :file:`stethoscope/api/defaults.py`.

Generic Configuration
^^^^^^^^^^^^^^^^^^^^^

Some configuration variables are shared across all types of practices:

- ``DISPLAY_TITLE``: The name to display in the Stethoscope UI.
- ``DESCRIPTION``: A short summary of the practice and why it's important.
- ``LINK`` (optional): A link to more information.
- ``NA_PLATFORMS`` (optional): A list of hardware platforms for which this practice isn't applicable
  (e.g., setting this to ``['iOS', 'Android']`` would prevent the practice from counting against
  mobile devices, as might be the case for software that's only available for PCs and Macs).
- ``PLATFORM_REQUIRED`` (optional; defaults to ``False``): If the platform isn't present in the
  information available for the device, consider this practice non-applicable for this device if
  this value is ``True``.

Installed Software
^^^^^^^^^^^^^^^^^^

:py:class:`InstalledSoftwarePractice` checks whether the specified software is installed.

Configuration
'''''''''''''

- ``SOFTWARE_NAMES``: A list of names to search for in the installed software (e.g., ``['Carbon
  Black Sensor']``).
- ``SERVICE_NAMES``: A list of service names to search for among running services (e.g.,
  ``['com.carbonblack.daemon']``).


.. _installed-software-example:

Example
'''''''

.. code:: py

  'carbonblack': {
    'SOFTWARE_NAMES': ['Carbon Black Sensor'],
    'SERVICE_NAMES': ['com.carbonblack.daemon'],
    'DISPLAY_TITLE': 'Carbon Black',
    'DESCRIPTION': (
      "Carbon Black is part of our approach to preventing and detecting malware "
      "infections. Installing Carbon Black helps protect your system and helps us "
      "detect when a system has been compromised, and how, so we can respond quickly and "
      "effectively."
    ),
    'LINK': '#',
    'PLATFORM_REQUIRED': True,
    'NA_PLATFORMS': ['iOS', 'Android'],
  },


Adding a Software Practice
''''''''''''''''''''''''''

To add a new software practice, one would register an entry point with a unique tag for the software
(e.g., ``mysoftware``) as in :file:`setup.py` and set the entry point's target to be
``stethoscope.plugins.pratices:InstalledSoftwarePractice``. Second, one would add the appropriate
values under the ``mysoftware`` key in the ``PRACTICES`` section of their config file (as in
:ref:`installed-software-example` above).



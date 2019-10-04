Configuration file
==================

Config file keys
----------------

The JSON configuration file has the following required sections:

.. _patterns:

patterns
^^^^^^^^

Specifies the regex patterns used to find files. The patterns must be in `python style regex`_.
Group names should be specified corresponding to the :ref:`page_keys` and :ref:`files`/filter parameters.
If an array is given for a pattern instead of a string, then `pybids`_ is used instead of regex. See :ref:`bids_section`
below.

For example, suppose we have an input and an output folder::

  .in
  ├── sub-1
  │   ├── anat
  │   │   ├── sub-1_T1w.nii
  │   │   └── sub-1_acq-fast_T1w.nii
  ├── sub-2
  │   └── anat
  │       └── sub-2_T1w.nii
  └── MNI152.nii

  .out
  ├── sub-1
  │   ├── BET
  │   │   ├── sub-1_bet.nii
  │   │   └── sub-1_acq-fast_bet.nii
  │   ├── classify
  │   │   ├── sub-1_dseg.nii
  │   │   └── sub-1_acq-fast_dseg.nii
  │   ├── logs
  │   │   └── sub-1_acq-fast
  │   │       └── crash.pklz
  └── sub-2
      ├── BET
      │   └── sub-2_bet.nii
      └── classify
          └── sub-2_dseg.nii
    
where we have multiple subjects, and some subjects also have a "fast" acquisition. Then we might have

.. literalinclude:: ../tests/testconfdocs.json
   :lines: 2-6

The "derivatives" pattern will match files in the subject folders,
"models" pattern will match files in the root directory, and "crash"
will match crash files (in this case only 1).
(We can pass both "in"
and "out" to the program on the command line, so both directories will
be searched.)

.. _bids_section:

bids
""""

The "derivatives" pattern above closely follows the `BIDS`_ specification.
As such we can instead use `pybids`_ to search for files. To signal that
we wish to use `pybids`_, we pass an array instead of a string:

.. literalinclude:: ../tests/testconfdocsbids.json
   :lines: 2-6

The contents of the array are passed to :py:class:`BIDSLayout` as the "config" parameter.
It may either be the name of a default configuration (at the time of this writing, either "bids" or "derivatives"),
a filename, or a JSON object. In the above example, the basic "bids" configuration
is all that is required.

.. _page_keys:

page_keys
^^^^^^^^^


These are the unique keys which identify a single QC page. The keys correspond to regex group names in :ref:`patterns`.
Continuing with the example above, if
we have multiple subjects and acquisition types, and we want a different QC page for each subject/acquisition combination,
we would have

.. literalinclude:: ../tests/testconfdocs.json
   :lines: 7-10

.. _page_filename_template:

page_filename_template
^^^^^^^^^^^^^^^^^^^^^^

Template output string for each qc page. :ref:`page_keys` may be used as
arguments (e.g., if "subject" is a page key, then one could have
"{subject}_QC.html"). If a bracket pair ("[...]") is used, and inside
that bracket is only one keyword argument, the section inside
the brackets will be used only if that argument is not :py:obj:`None`.
This syntax was inspired by `pybids`_.

Using the above example if we have

.. literalinclude:: ../tests/testconfdocs.json
   :lines: 11

We will have the following output files

* ``sub-1_QC.html``
* ``sub-1_acq-fast_QC.html``
* ``sub-2_QC.html``


.. _index_filename:

index_filename
^^^^^^^^^^^^^^

A string giving the name of the output index file, i.e., the file
containing a list of all the QC pages.


.. literalinclude:: ../tests/testconfdocs.json
   :lines: 12

   
.. _files:

files
^^^^^

A json object where each key identifies a file (for a given QC page),
and the values are objects describing how to identify the file. For
example

.. literalinclude:: ../tests/testconfdocs.json
   :lines: 13-36

The above example defines 5 files, "T1", "BET", "classified",
"MNI", and "crashfiles". "T1", "BET", and "classified" follow the regex in :ref:`patterns`/derivatives.
In this case each is uniquely identified as having a specific suffix,
where suffix is a group name in
the "derivatives" pattern.
The filter parameters must uniquely identify a
file for each QC page (in this case each sub/acq combination). If
multiple files match a pattern, or if a file is detected multiple
times (e.g., if the same file is found for both "BET" and
"classified"), the program will throw an error.

"MNI" is identified as having the base "MNI152". However, this is not
necessary, as there are no other files that could match the "model"
pattern. Note that this file is the same for all sub/acq combinations,
i.e., it is the same for each QC page. Therefore, we set the "global"
attribute to true. (Without setting global, the program will not be able
to determine which subj/acq combination "MNI" belongs to, and will fail.)

"crashfiles" matches the pattern "crash". Setting "allow_multiple" to true
allows multiple files to match the pattern, which are stored in a list.


.. _reportlets:
   
reportlets
^^^^^^^^^^

This section specifies the elements of the QC page. It is a list of objects,
where each object has a "type" key and then a key/value pair for each parameter
to the reportlet indicated by "type".

.. literalinclude:: ../tests/testconfdocs.json
   :lines: 37-56

All key/value pairs besides "type" are sent to the corresponding :doc:`reportlet interface </interfaces>`.

Final
-----

The final config file is then:

.. literalinclude:: ../tests/testconfdocs.json


Global
------

The optional config section "global_reportlet_settings" may contain settings
that are applied to all reportlets (but do not override individually set values).
Currently, these may be "image_width", "image_height", and "contour_width".


Schema
------

The configuration file has the following schema

.. literalinclude:: ../PipelineQC/schema/config.json

.. _python style regex: https://docs.python.org/3.5/library/re.html#regular-expression-syntax
.. _pybids: https://bids-standard.github.io/pybids/
.. _bids: https://bids-specification.readthedocs.io/en/stable/

Configuration file
==================

The JSON configuration file has the following required keys:

.. _patterns:

patterns
--------

Specifies the regex patterns used to find files. The patterns must be in python style regex.
Group names should be specified corresponding to the "page_keys" and "filter" parameters.

For example if our output folder has the following structure::

  .out
  ├── sub-1
  │   ├── BET
  │   │   ├── sub-1_bet.nii
  │   │   └── sub-1_acq-fast.nii
  │   └── classify
  │       ├── sub-1_dseg.nii
  │       └── sub-1_acq-fast_dseg.nii
  └── sub-2
      ├── BET
      │   └── sub-2_bet.nii
      └── classify
          └── sub-2_dseg.nii

    
where we have multiple subjects, and some subjects also have a "fast" acquisition. Then we might have

.. code-block:: javascript
   
   |patterns|

blah
    
.. |patterns| replace::
   "patterns": {
   pattern1": "sub-(?P<sub>[a-zA-Z0-9]+)/(?P<dir>[^/]*)/sub-(?P=sub)(_acq-(?P<acq>[a-zA-Z0-9]+))?_(?P<suffix>[a-zA-Z0-9]+)\\.nii"
   }


page_keys
---------


The unique keys which identify a single QC page. The keys correspond to regex group names in :ref:`patterns`.
Continuing with the example above, if
we have multiple subjects and acquisition types, and we want a different QC page for each subject/acquisition combination,
we could have

.. code-block:: javascript

   "page_keys": [
       "sub",
       "acq"
   ],

page_filename_template
----------------------

Template output string for each qc page. page_keys may be used as
arguments (e.g., if "sub" is a page key, then one could have
"{sub}_QC.html"). If a bracket pair ("[...]") is used, and inside
that bracket contains only one keyword argument, the section inside
the brackets will be used only if that argument is not :py:obj:`None`.

Using the above example if we have

.. code-block:: javascript

   "page_filename_template": "sub-{sub}[_acq-{acq}]_QC.html",

We will have the following output files

* ``sub-1_QC.html``
* ``sub-1_acq-fast_QC.html``
* ``sub-2_QC.html``


index_filename
--------------

A string giving the name of the output index file, i.e., the file
containing a list of all the QC pages.

.. code-block:: javascript

   "index_filename": "QC_index.html",

asd 

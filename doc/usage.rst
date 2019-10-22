Usage
=====

.. argparse::
   :prog: PipelineQC
   :module: PipelineQC.main
   :func: get_parser
   :nosubcommands:

qcpages
^^^^^^^

.. argparse::
   :prog: PipelineQC
   :module: PipelineQC.main
   :func: get_parser
   :path: qcpages

   config_file : @replace
	  See the :doc:`Configuration file</config>` section

combine
^^^^^^^

.. argparse::
   :prog: PipelineQC
   :module: PipelineQC.main
   :func: get_parser
   :path: combine

image
^^^^^^^

.. argparse::
   :prog: PipelineQC
   :module: PipelineQC.main
   :func: get_parser
   :path: image

findfiles
^^^^^^^^^
.. argparse::
   :prog: PipelineQC
   :module: PipelineQC.main
   :func: get_parser
   :path: findfiles

   config_file : @replace
	  See the :doc:`Configuration file</config>` section

index
^^^^^^^

.. argparse::
   :prog: PipelineQC
   :module: PipelineQC.main
   :func: get_parser
   :path: index

=====================
Hackwork: Gayson
=====================

https://github.com/serioeseGmbH/hackwork-gayson

hackwork_gayson is a library to help with persisting data to and reading data from the database (i.e. a JSONField)
by defining JSON conversion for additional Python types.

Quick start
-----------

1. Install the package with pip::

    pip install hackwork-gayson

2. Import ``gayson.Convert``. It provides class methods ``value_to_json`` and ``json_to_value``.

3. Convert away.

4. Optionally, derive your own subclasses of Converter to add to the conversion capabilities.
   Keep in mind that the conversion will only be available when your additional subclasses are imported.
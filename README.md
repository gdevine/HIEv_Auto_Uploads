# HIEv Auto Uploads
Python script to perform automated data uploads into the HIEv application.
Using this script, a user can dump files (with a file naming convention applied) into the 
Data directory and use the file_settings.yaml file to specify regex matching patterns against 
those files. Upon successful upload into HIEv the matched files are moved out of the Data directory
and into the Backups folder.   

This script expects a folder named 'Data' and a folder named 'Backups' at the same level as this 
script to work.

On Windows, both pyyaml and requests libraries will need to be installed on the system, e.g by using 'pip install'.

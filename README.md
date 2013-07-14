## Description ##
Service directory. A listing of services available on the mesh.

## Usage ##
###sysadmins###
* run ```/opt/byzantium/service_index/services.py``` to manually start.

###users###
* browse to ```http://byzantium.mesh``` to view the available services

### service providers ###
* avahi records that match the filters in place with ```show=user``` on it's own line of the txt record of the avahi service will be displayed to users.
* txt records with ```appendtourl=<stuff>``` on it's own line of the txt record will append ```<stuff>``` to the url used to make the link.
* txt records with ```description=<stuff>`` will take everything following the equals sign to the next token or the end of the string and use it as the description in the entry on the service directory.

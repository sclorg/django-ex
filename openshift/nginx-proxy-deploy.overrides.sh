# ================================================================================================================
# Special Deployment Parameters needed for injecting a user supplied white-list into the deployment configuration
# ----------------------------------------------------------------------------------------------------------------
# The results need to be encoded as OpenShift template parameters for use with oc process.
# ================================================================================================================

# Define the name of the override param file.
_overrideParamFile=$(basename ${0%.*}).param

# Ask the user to supply the list of IP addresses ...
read -r -p $'\n\033[1;33mEnter the white list of trusted IP addresses that should be allowed to access the SiteMinder route (as a space delimited list of IP addresses):\033[0m\n' SITEMINDER_WHITE_LIST

# Write the results into a param file, since you can't pass space delimited parameters on the command line using -p or --param
echo "SITEMINDER_WHITE_LIST=${SITEMINDER_WHITE_LIST}" > ${_overrideParamFile}

SPECIALDEPLOYPARMS="--param-file=${_overrideParamFile}"
echo ${SPECIALDEPLOYPARMS}
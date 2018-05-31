# =================================================================
# Special Deployment Parameters needed for Application  Deployment
# -----------------------------------------------------------------
# The results need to be encoded as OpenShift template
# parameters for use with oc process.
# =================================================================

generateUsername() {
  # Generate a random username and Base64 encode the result ...
  _userName=USER_$( cat /dev/urandom | LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 4 | head -n 1 )
  _userName=$(echo -n "${_userName}"|base64)
  echo ${_userName}
}

generatePassword() {
  # Generate a random password and Base64 encode the result ...
  _password=$( cat /dev/urandom | LC_CTYPE=C tr -dc 'a-zA-Z0-9_' | fold -w 16 | head -n 1 )
  _password=$(echo -n "${_password}"|base64)  
  echo ${_password}
}

_userName=$(generateUsername)
_password=$(generatePassword)

read -r -p $'\n\033[1;33mEnter the network of the upstream proxy (in CIDR notation; for example 0.0.0.0/0); defaults to 0.0.0.0/0:\033[0m\n' PROXY_NETWORK
if [ -z "${PROXY_NETWORK}" ]; then
  PROXY_NETWORK="0.0.0.0/0"
fi

SPECIALDEPLOYPARMS="-p PROXY_NETWORK=${PROXY_NETWORK} -p BASICAUTH_USERNAME=${_userName} -p BASICAUTH_PASSWORD=${_password}"
echo ${SPECIALDEPLOYPARMS}


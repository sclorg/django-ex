# ========================================================================
# Special Deployment Parameters needed for the backup instance.
# ------------------------------------------------------------------------
# The generated config map is used to update the Backup configuration.
# ========================================================================

CONFIG_MAP_NAME=backup-conf
SOURCE_FILE=./config/backup.conf
OUTPUT_FORMAT=json
OUTPUT_FILE=backup-conf-configmap_DeploymentConfig.json

generateConfigMap() {  
  _config_map_name=${1}
  _source_file=${2}
  _output_format=${3}
  _output_file=${4}
  if [ -z "${_config_map_name}" ] || [ -z "${_source_file}" ] || [ -z "${_output_format}" ] || [ -z "${_output_file}" ]; then
    echo -e \\n"generateConfigMap; Missing parameter!"\\n
    exit 1
  fi

  oc create configmap ${_config_map_name} --from-file ${_source_file} --dry-run -o ${_output_format} > ${_output_file}
}

generateConfigMap "${CONFIG_MAP_NAME}" "${SOURCE_FILE}" "${OUTPUT_FORMAT}" "${OUTPUT_FILE}"

SPECIALDEPLOYPARMS=""
echo ${SPECIALDEPLOYPARMS}


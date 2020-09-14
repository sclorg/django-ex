from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
	# Error was occuring becauase vue.js doesn't always output chunk-common.js 
	# Solution from https://stackoverflow.com/a/51580328/2616170
    manifest_strict = False
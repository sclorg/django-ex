module.exports = {
  outputDir: '../edivorce/apps/core/static/dist/vue',
  filenameHashing: false,
  runtimeCompiler: true,
  pages: {
    filingUploader: {
      entry: 'src/pages/filing-uploader/main.js',
      template: 'public/filing-uploader.html',
      filename: 'index.html',
      chunks: ['chunk-vendors', 'chunk-common', 'filingUploader']
    }
  },
  configureWebpack: {
    optimization: {
      splitChunks: {
        minSize: 1
      }
    }
  }
}
module.exports = {
  outputDir: '../edivorce/apps/core/static/dist/vue',
  filenameHashing: false,
  runtimeCompiler: true,
  pages: {
    initialFiling: {
      entry: 'src/pages/initial-filing/main.js',
      template: 'public/initial-filing.html',
      filename: 'index.html',
      chunks: ['chunk-vendors', 'chunk-common', 'initialFiling']
    },
    finalFiling: {
      entry: 'src/pages/final-filing/main.js',
      template: 'public/final-filing.html',
      filename: 'final-filing.html',
      chunks: ['chunk-vendors', 'chunk-common', 'finalFiling']
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
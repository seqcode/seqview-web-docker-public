module.exports = (env, argv) => ({
  mode: argv.mode === 'production' ? 'production' : 'development',
  output: {
    path: argv.mode === 'production' ? `${__dirname}/dist/` : '/usr/src/seqview/static/frontend/',
    publicPath: "http://laxmi.vmhost.psu.edu/static/frontend/",
    filename: "main.js",
  },
  //devtool: 'inline-source-map',
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
		loader: ["react-hot-loader/webpack", require.resolve('babel-loader')],
    	//options: {
            // This is a feature of `babel-loader` for webpack (not Babel itself).
            // It enables caching results in ./node_modules/.cache/babel-loader/
            // directory for faster rebuilds.
		//	cacheDirectory: true,
			//plugins: ['react-hot-loader/babel'],
        //},
        //use: {
        //  loader: 'babel-loader',
        //}
      },
      { 
        test: /\.css$/, 
        use: ['style-loader', 'css-loader'] 
      },
      { test: /\.(png|woff|woff2|eot|ttf|svg)$/, loader: 'url-loader?limit=100000'   },
     ],
  },
  devServer: {
	host: "0.0.0.0",
	port: "80",
    writeToDisk: true,
	disableHostCheck: true,
	hot: true,
	inline: true,
  },
  externals: {
    'Config': JSON.stringify(require('./seqviewConfig.js'))
  },
});

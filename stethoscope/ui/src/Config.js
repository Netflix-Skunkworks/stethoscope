let config = require('../config.defaults.json')
config = Object.assign(config, require('../config.json'))

// set the cookie if it's provided
if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_TOKEN) {
  document.cookie = `token=${process.env.REACT_APP_TOKEN}`
  console.log('set token to', process.env.REACT_APP_TOKEN)
}

export default config

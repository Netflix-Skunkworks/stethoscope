let config = require('../config.defaults.json')
config = Object.assign(config, require('../config.json'))

// also apply environment variable overrides, if present
if (process.env.REACT_APP_CONFIG && process.env.REACT_APP_CONFIG.trim() !== '') {
  try {
    const moreConfig = JSON.parse(process.env.REACT_APP_CONFIG)
    config = Object.assign(config, moreConfig)
  } catch (e) {
    console.log("Error applying more config from environment variables:", e)
  }
}

// set the cookie if it's provided
if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_TOKEN) {
  document.cookie = `token=${process.env.REACT_APP_TOKEN}`
  console.log('set token to', process.env.REACT_APP_TOKEN)
}

export default config

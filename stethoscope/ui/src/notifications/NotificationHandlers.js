if (typeof global.stethoscopeNotificationHandlers === 'undefined') {
  global.stethoscopeNotificationHandlers = []
}

const components = global.stethoscopeNotificationHandlers

function register(component) {
  components.push(component)
}

function all() {
  return components
}

function getComponentForData (data) {
  const components = all()
  for (let i = 0; i < components.length; i++) {
    const c = components[i]
    if (c.handles(data)) return c
  }
}

module.exports = { register, all, getComponentForData }
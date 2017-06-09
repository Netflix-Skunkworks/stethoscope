export function criticalOnly (devices) {
  return devices ? devices.filter((d) => d.deviceRating === 'critical') : []
}

export function criticalDeviceSummary (devices) {
  const criticalDevices = criticalOnly(devices)
  if (criticalDevices.length > 0) {
    const count = criticalDevices.length
    const pluralizedDevices = 'device' + (count !== 1 ? 's' : '')
    const pluralizedRequires = 'require' + (count === 1 ? 's' : '')
    const devicesList = criticalDevices.map(function (d) {
      return d.model || d.manufacturer
    }).join(', ')

    return {
      count,
      pluralizedDevices,
      pluralizedRequires,
      devicesList
    }
  }

}

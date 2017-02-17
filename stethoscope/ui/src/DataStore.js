import 'whatwg-fetch'
import sortBy from './utils/sortby'

const fetch = window.fetch

class DataStore {

  constructor () {
    this.loadDevices = this.loadDevices.bind(this)
    this.loadAccounts = this.loadAccounts.bind(this)
    this.loadNotifications = this.loadNotifications.bind(this)
  }

  tooOld (device) {
    // filter out if older than 30 days
    var sync = new Date(device.last_sync)
    return Date.now() - sync.getTime() > 30 * 24 * 60 * 60 * 1000
  }

  filterDevices (rawDevices, opts) {
    if (!opts) opts = {}
    let devices = rawDevices.filter(function (device) {
      if (device.status === 'E-Waste') return false
      if (typeof device.last_sync === 'undefined') {
        return false
      } else if (this.tooOld(device) && !opts.skipOldFilter) {
        return false
      }
      return true
    }.bind(this))

    // get some high level info
    devices.forEach(function (d) {
      // sorting by criticality
      d.critical = []
      d.suggested = []
      d.done = []
      d.unknown = []

      const practices = Object.values(d.practices)
      // group by severity
      practices.forEach(function (p) {
        // hide SentinelOne in the UI
        if (p.title === 'SentinelOne') return
        if (p.status === 'warn') {
          d.critical.push(p)
        } else if (p.status === 'nudge') {
          d.suggested.push(p)
        } else if (p.status === 'ok') {
          d.done.push(p)
        }
      })

      if (d.critical.length > 0) {
        d.deviceRating = 'critical'
      } else if (d.suggested.length > 0) {
        d.deviceRating = 'warning'
      } else if (d.critical.length + d.suggested.length + d.done.length === 0) {
        d.deviceRating = 'unknown'
      } else {
        d.deviceRating = 'ok'
      }
    })

    // mark devices we think are duplicates
    devices.forEach(function (d) {
      // if we don't have an identifier, then match to others based on model
      if (!d.identifiers.serial && !d.identifiers.mac_addresses) {
        d.unknownDevice = true
        // look for a match based on model
        const possibleMatches = devices.filter((otherDevice) => d.model === otherDevice.model && otherDevice.identifiers.serial)
        d.possibleMatch = possibleMatches.length > 0 ? possibleMatches[0] : null
      }
    })

    // and sort critical devices to the top
    devices = sortBy(devices, (d) => d.last_sync).reverse()
    devices = sortBy(devices, (d) => {
      switch (d.deviceRating) {
        case 'critical': return 2
        case 'warning': return 1
        case 'ok': return 0
        default: return -1
      }
    }).reverse()

    return devices
  }

  loadDevices (email) {
    const isTestData = process.env.NODE_ENV === 'development' && email.match(/@example\.com$/)
    return fetch(`/api/v1/devices/merged/${email}`, { credentials: 'same-origin' }).then(function (response) {
      return response.json()
    }).then(function (data) {
      return Promise.resolve(this.filterDevices(data, { skipOldFilter: isTestData }))
    }.bind(this))
  }

  loadAccounts (email) {
    return fetch(`/api/v1/accounts/merged/${email}`, { credentials: 'same-origin' }).then(function (response) {
      return response.json()
    })
  }

  loadNotifications (email) {
    return fetch(`/api/v1/notifications/merged/${email}`, { credentials: 'same-origin' }).then(function (response) {
      return response.json()
    })
  }

}

export default DataStore

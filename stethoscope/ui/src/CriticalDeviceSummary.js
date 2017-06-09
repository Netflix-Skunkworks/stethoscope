import React from 'react'
import { criticalDeviceSummary } from './utils/device-filter'

export default (props) => {
  const devices = props.devices || props.store.devices
  if (!devices) return null
  const summary = criticalDeviceSummary(devices)

  if (summary) {
    return <div>
      You have <span className='text-danger'>{summary.count}</span> {summary.pluralizedDevices} that {summary.pluralizedRequires} attention:
      &nbsp;
      <span className='text-danger'>
        {summary.devicesList}
      </span>
    </div>
  } else {
    return null
  }

}

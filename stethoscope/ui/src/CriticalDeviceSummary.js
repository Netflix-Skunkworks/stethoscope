import React from 'react'
import { criticalDeviceSummary } from './utils/device-filter'
import Accessible from './Accessible'

export default (props) => {
  const devices = props.devices || props.store.devices
  if (!devices) return null
  const summary = criticalDeviceSummary(devices)

  if (summary) {
    return (
      <Accessible role='alert' live='assertive'>
        <p>
          You have <span className='text-danger'>{summary.count}</span> {summary.pluralizedDevices} that {summary.pluralizedRequires} attention:
          &nbsp;
          <span className='text-danger'>
            {summary.devicesList}
          </span>
        </p>
      </Accessible>
    )
  } else {
    return null
  }
}

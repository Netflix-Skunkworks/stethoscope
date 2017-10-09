import React, { Component } from 'react'
import fecha from 'fecha'
import Timeago from 'timeago.js'
import Accessible from './Accessible'
import Action from './Action'
import './Device.css'
import Config from './Config'

const ta = new Timeago()

let formatTime = function (t) {
  return ta.format(t)
}

let longFormatTime = function (t) {
  return fecha.format(new Date(t), 'dddd, MMMM Do YYYY [at] h:mm a')
}

class Device extends Component {

  constructor (props) {
    super(props)
    this.state = {
      showInfo: false
    }
    this.toggleInfo = this.toggleInfo.bind(this)
  }

  actions (actions, type) {
    return actions.map((a) =>
      <Action key={a.title} type={type} action={a} />
    )
  }

  process (device) {
    let d = Object.assign({}, device)

    d.friendlyName = d.model || d.manufacturer || 'Unknown device'
    d.identifier = d.name || d.identifiers.serial || (d.identifiers.mac_addresses || []).join(' ')

    return d
  }

  toggleInfo () {
    this.setState({
      showInfo: !this.state.showInfo
    })
  }

  render () {
    if (!this.props.device) return null

    const device = this.process(this.props.device)

    let deviceInfo = null
    let possibleMatch = null
    let unknownDevice = null
    let noModel = null

    if (this.state.showInfo) {
      deviceInfo = (
        <div className='deviceInfo'>
          <dl className='device-info'>
            <dt>Type</dt><dd>{device.type}&nbsp;</dd>
            <dt>Manufacturer</dt><dd>{device.manufacturer}&nbsp;</dd>
            <dt>Model</dt><dd>{device.model}&nbsp;</dd>
            <dt>Platform</dt><dd>{device.platform}&nbsp;</dd>
            <dt>OS Version</dt><dd>{device.os_version}&nbsp;</dd>
            <dt>Name</dt><dd>{device.name}&nbsp;</dd>
            <dt>MAC addresses</dt>
            <dd>
              <ul className='mac-addresses'>
                {
                  device.identifiers.mac_addresses &&
                    device.identifiers.mac_addresses.map((mac, i) =>
                      <li key={i}>{mac}</li>
                    )
                }
              </ul>
            </dd>
            <dt>Serial</dt><dd>{device.identifiers.serial}&nbsp;</dd>
            <dt>UDID</dt><dd>{device.identifiers.udid}&nbsp;</dd>
            <dt>Status</dt><dd>{device.status}&nbsp;</dd>
          </dl>
        </div>
      )
    }

    if (device.possibleMatch) {
      possibleMatch = <div className='possible-match'>This may be the same device as {device.possibleMatch.model} ({device.possibleMatch.identifiers.serial})</div>
    }

    if (device.unknownDevice) {
      const sources = device.sources.map((d) => Config.sourceLabels[d] || d)

      unknownDevice = <div>
        {possibleMatch}
        <p className='unknown-device-warning'>
          No information is available about the security state of this device.
        </p>
        <p className='unknown-device-warning'>
          It was detected via {sources.join(', ')}.
        </p>
        <p className='unknown-device-warning'>
          If you are concerned about this, you can check your Google-connected devices
          and disable any you are no longer using.
        </p>
        <a href='https://security.google.com/settings/security/activity' target='_blank'>Review devices</a>
      </div>
    }

    if (!device.model) {
      let mailLink = '?Subject=Unknown device'
      if (device.identifiers && device.identifiers.mac_addresses) mailLink += ` ${device.identifiers.mac_addresses.join(' ')}`
      noModel = (
        <div>
          <p className='unknown-device-warning'>
            This device was seen on the {Config.orgName} network, logged in with your credentials,
            on {longFormatTime(device.last_sync)}.
          </p>
          <p className='unknown-device-warning'>
            If this seems suspicious to you, please email <a href={`mailto:${Config.contactEmail}${mailLink}`}>{Config.contactEmail}</a>.
          </p>
        </div>
      )
    }

    return (
      <div className='device-wrapper'>
        <div className={`panel device ${device.deviceRating}`}>
          <header>
            <div className='device-name'>{device.friendlyName}</div>
            <div className='device-identifier'>{device.identifier}&nbsp;</div>
            <Accessible expanded={this.state.showInfo} label={`Toggle and review ${device.deviceRating} device information for ${device.friendlyName}`}>
              <a className={`device-info-toggle ${this.state.showInfo ? 'open' : 'closed'}`} onClick={this.toggleInfo}>&#9660;</a>
            </Accessible>
          </header>

          {deviceInfo}

          <div className='action-list'>

            <ul>
              { this.actions(device.critical, 'critical') }
              { this.actions(device.suggested, 'suggested') }
              { this.actions(device.done, 'done') }
            </ul>

          </div>

          {unknownDevice}

          {noModel}

          <div className='last-updated'>Last updated {formatTime(device.last_sync)}</div>

        </div>
      </div>
    )
  }
}

export default Device

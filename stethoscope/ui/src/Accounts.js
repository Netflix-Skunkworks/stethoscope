import React, { Component } from 'react'
import Action from './Action'
import Spinner from './Spinner'
import './Accounts.css'
import Config from './Config'

class Accounts extends Component {
  render () {
    if (this.props.store.accounts) {
      if (this.props.store.accounts.length > 0) {
        return (
          <div id='account-list'>
            {this.props.store.accounts.map((a) => <Account account={a} key={a.source} />)}
          </div>
        )
      } else {
        return <div className='panel'>No accounts found for <strong>{this.props.store.email}</strong>.</div>
      }
    } else if (this.props.store.accounts === false) {
      return null
    } else {
      return <div>
        <Spinner>Loading account data...</Spinner>
      </div>
    }
  }
}

class Account extends Component {

  render () {
    const account = this.props.account
    const twoFactorType = account.user_usage['accounts:is_2sv_enrolled'] ? 'done' : 'critical'
    const twoFactorAction = {
      title: '2-Step Verification',
      link: 'https://www.google.com/landing/2step'
    }

    return (
      <div className='account-wrapper'>
        <div className={`panel account ${twoFactorType}`}>
          <header>
            <div className='account-type'>{account.type}</div>
            <div>{account.name}</div>
          </header>

          <ul>
            <Action type={twoFactorType} action={twoFactorAction}>
              &#8220;2-Step Verification&#8221; is the name Google uses for <i>two-factor
                authentication</i>, which is the practice of requiring two different methods of
              authentication to prove identity. Typically, the factors available are something you
              <i>know</i> (password, PIN), something you <i>have</i> (phone, Yubikey, badge), or something
              you <i>are</i> (photo, fingerprint, retina scan, DNA). Enabling 2-Step Verification helps
              prevent unauthorized access to your account by requiring a second factor in certain
              situations (such as logging in from a new computer or location).
            </Action>
          </ul>

          <p>
            We recommend that you <a href='https://security.google.com/settings/security/permissions' target='_blank'>check
            which applications are connected</a> to your {Config.orgName} Google account and remove permissions for anything that you don't recognize or no longer need.
          </p>

        </div>
      </div>
    )
  }
}

export default Accounts

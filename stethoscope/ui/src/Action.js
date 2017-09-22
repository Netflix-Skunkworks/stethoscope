import React, { Component } from 'react'
import Accessible from './Accessible'

class ActionIcon extends Component {

  constructor (props) {
    super(props)
    const styleProps = {
      color: props.color,
      width: props.width,
      height: props.height
    }
    const style = Object.assign({}, {pointerEvents: 'none', display: 'block', width: '100%', height: '100%'}, styleProps)
    this.icons = {
      checkmark: <svg viewBox='0 0 64 64' preserveAspectRatio='xMidYMid meet' style={style}><path fill={style.color} d='M54 8l-30 30-14-14-10 10 24 24 40-40z' /></svg>,
      blocked: <svg viewBox='0 0 64 64' preserveAspectRatio='xMidYMid meet' style={style}><path fill={style.color} d='M54.627 9.373c-6.044-6.044-14.080-9.373-22.628-9.373s-16.583 3.329-22.628 9.373c-6.044 6.044-9.373 14.080-9.373 22.627s3.329 16.583 9.373 22.627c6.044 6.044 14.080 9.373 22.628 9.373s16.583-3.329 22.628-9.373c6.044-6.044 9.373-14.080 9.373-22.628s-3.329-16.583-9.373-22.628zM56 32c0 5.176-1.647 9.974-4.444 13.899l-33.454-33.454c3.925-2.797 8.723-4.444 13.899-4.444 13.234 0 24 10.766 24 24zM8 32c0-5.176 1.647-9.974 4.444-13.899l33.454 33.454c-3.925 2.797-8.723 4.444-13.899 4.444-13.234 0-24-10.766-24-24z' /></svg>
    }
  }

  render () {
    return (
      <span className='action-icon' title={this.props.title}>
        {this.icons[this.props.name]}
      </span>
    )
  }
}

class Action extends Component {
  constructor (props) {
    super(props)
    this.state = {
      showDescription: false
    }
    this.toggleDescription = this.toggleDescription.bind(this)
  }
  hoverText (type) {
    var hoverTextLabels = {
      critical: 'Highly recommended action',
      suggested: 'Suggested action',
      done: 'Completed action'
    }
    return hoverTextLabels[type]
  }
  iconName (type) {
    if (type === 'critical' || type === 'suggested') {
      return 'blocked'
    } else if (type === 'done') {
      return 'checkmark'
    }
  }
  iconColor (type) {
    if (type === 'critical') {
      return '#a94442'
    } else if (type === 'done') {
      return '#bbd8ca'
    } else if (type === 'suggested') {
      return '#bfa058'
    }
  }

  toggleDescription () {
    this.setState({
      showDescription: !this.state.showDescription
    })
  }

  render () {
    const action = this.props.action
    const type = this.props.type
    let description = null
    if (this.state.showDescription) {
      description = (
        <div>
          <div className='more-info'>
            <p className='description'>
              {action.description}
              {this.props.children}
            </p>
            { action.details &&
              <pre className='description'>{action.details}</pre>
            }
            { action.link &&
              <a href={action.link} target='_blank'>More info</a>
            }
          </div>
        </div>
      )
    }
    return (
      <li className={type}>
        <span className='title' onClick={this.toggleDescription}>
          <ActionIcon className='action-icon' name={this.iconName(type)} color={this.iconColor(type)} title={this.hoverText(type)} width='18px' height='18px' />
          {action.title}
        </span>
        <Accessible label='Toggle action description' expanded={this.state.showDescription}>
          <a className={`toggleLink show-description ${this.state.showDescription ? 'open' : 'closed'}`} onClick={this.toggleDescription}>&#9660;</a>
        </Accessible>
        {description}
      </li>
    )
  }
}

export default Action

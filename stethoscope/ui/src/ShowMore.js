import React, { Component } from 'react'

class ShowMore extends Component {
  constructor (opts) {
    super(opts)
    this.state = {
      expanded: false
    }
  }
  toggle (evt) {
    evt.preventDefault()
    this.setState({ expanded: !this.state.expanded })
  }
  render () {
    const linkText = this.state.expanded ? (this.props.hideText || 'hide') : (this.props.showText || 'show more')
    const link = <a className='toggle-details' href='#' onClick={(evt) => this.toggle(evt)}>{linkText}</a>
    let content
    if (this.state.expanded) content = <div>{this.props.children}</div>
    return (<div>
      {link}
      {content}
    </div>)
  }
}

export default ShowMore

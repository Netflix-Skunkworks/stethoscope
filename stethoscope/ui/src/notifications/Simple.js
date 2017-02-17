import React, { Component } from 'react'

class SimpleNotification extends Component {

  constructor (opts) {
    super(opts)
    this.state = {
      showComment: false
    }
  }

  dismiss () {
    if (this.props.onDismiss) this.props.onDismiss()
  }

  render () {
    return (
      <div>
        <p>{this.props.data.message}</p>
        <button className={`btn btn-success`} onClick={() => this.dismiss()}>Ok</button>
      </div>
    )
  }
}

SimpleNotification.handles = function (data) {
  return data.type === 'simple'
}

export default SimpleNotification

import React from 'react'
import PropTypes from 'prop-types'

/**
* The main benefit of this component is adding keyboard handlers and tabIndex to your
* non accessible interactive components. If no props are passed, will assume role=button
* and will try to proxy an onClick event listener
*
* EXAMPLE
*  Starting component:
*    <a onClick={this.someAction}>Non-accessible component</a>
*
*  Using Accessible:
*   <Accessible label='Do something'>
*     <a onClick={this.someAction}>Non-accessible component</a>
*   </Accessible>
*
*  Output:
*    <a role="button" tabindex="0" aria-label="Do Something" onKeyPress={this.someAction} onClick={this.someAction}>Non-accessible component</a>
*/
export default class Accessible extends React.Component {
  constructor (props) {
    super(props)
    this.handle = this.handle.bind(this)
  }

  /**
   * returns an event listener on the child that will
   * trigger the provided action (default onClick) when user presses space
   * or enter key - ignores other keys
   * @param  {Function} action Probably a click handler used in the child component
   * @return {undefined}
   */
  handle (action) {
    return event => {
      if (event.keyCode && [13, 32].includes(event.keyCode)) {
        event.preventDefault()
        action(event)
      }
    }
  }

  render () {
    let {
      action = false,
      id,
      children,
      role,
      ...ariaProps
    } = this.props

    if (React.Children.count(children) !== 1) {
      throw new Error('Accessible expects one child component')
    }

    const accessibleProps = { id, role }
    const child = React.Children.only(children)

    // prefix additional props with `aria-${key}`
    for (let key in ariaProps) {
      if (!key.startsWith('aria-')) {
        accessibleProps[`aria-${key}`] = ariaProps[key]
      } else {
        accessibleProps[key] = ariaProps[key]
      }
    }
    // try to infer a label if not specified
    if (!accessibleProps['aria-label'] && child.props.title) accessibleProps['aria-label'] = child.props.title
    // try to infer action if none specified
    if (!action) action = child.props.onClick || false

    // if we were able to infer an event handler, attach listeners and tabIndex
    if (action) {
      Object.assign(accessibleProps, { onKeyDown: this.handle(action), tabIndex: 0 })
    }

    return React.cloneElement(child, accessibleProps)
  }
}

Accessible.defaultProps = {
  role: 'button'
}

Accessible.propTypes = {
  label: PropTypes.string,
  role: PropTypes.oneOf([
    'button', 'checkbox', 'dialog', 'gridcell', 'link', 'log', 'marquee',
    'menuitem', 'menuitemcheckbox', 'menuitemradio', 'option', 'progressbar',
    'radio', 'scrollbar', 'slider', 'spinbutton', 'status', 'tab', 'tabpanel',
    'textbox', 'timer', 'tooltip', 'treeitem', 'switch', 'alert'
  ]).isRequired,
  action: PropTypes.func
}

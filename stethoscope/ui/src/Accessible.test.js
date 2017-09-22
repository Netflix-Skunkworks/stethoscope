/* eslint-env mocha */
/* global expect */

import React from 'react'
import ReactDOM from 'react-dom'
import { mount } from 'enzyme'
import Accessible from './Accessible'

it('renders without crashing', () => {
  const div = document.createElement('div')
  ReactDOM.render(<Accessible><div /></Accessible>, div)
})

it('crashes if multiple children are passed', (done) => {
  const div = document.createElement('div')
  try {
    ReactDOM.render(
      <Accessible>
        <div />
        <div />
      </Accessible>
    , div)
  } catch (e) {
    return done()
  }
  throw new Error('Accessible should have crashed')
})

it('adds aria-* attributes to child component', () => {
  const wrapper = mount(<Accessible label='Test' expanded><div /></Accessible>)
  const el = wrapper.getDOMNode()
  expect(el.getAttribute('aria-label')).toEqual('Test')
  expect(el.getAttribute('aria-expanded')).toEqual('true')
})

it('adds space and enter handlers and allows original action', () => {
  let count = 0
  const onClick = () => count++
  const wrapper = mount(
    <Accessible label='Test' action={onClick}>
      <a onClick={onClick}>Click Me</a>
    </Accessible>
  )

  wrapper.simulate('keyDown', {keyCode: 13})
  expect(count).toEqual(1)

  wrapper.simulate('keyDown', {keyCode: 32})
  expect(count).toEqual(2)

  wrapper.simulate('click')
  expect(count).toEqual(3)
})

it('will infer action if none specified', () => {
  let count = 0
  const onClick = () => count++
  const wrapper = mount(
    <Accessible label='Test'>
      <a onClick={onClick}>Click Me</a>
    </Accessible>
  )

  wrapper.simulate('keyDown', {keyCode: 13})
  expect(count).toEqual(1)
})

it('adds tabIndex to interactive components', () => {
  let count = 0
  const onClick = () => count++
  const wrapper = mount(
    <Accessible label='Test' action={onClick}>
      <a onClick={onClick}>Click Me</a>
    </Accessible>
  )
  const el = wrapper.getDOMNode()
  expect(el.getAttribute('tabindex')).toEqual('0')
})

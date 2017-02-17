import React, { Component } from 'react'
import Config from './Config.js'

class Faq extends Component {
  render () {
    let faqContent = null
    if (Config.faq.googleDoc) {
      faqContent = <iframe src={Config.faq.googleDoc} />
    } else if (Config.faq.content) {
      const entries = Config.faq.content.map(function (entry) {
        return (
          <div className='faq-entry' key={entry.question}>
            <h3 className='faq-question'>{entry.question}</h3>
            <p className='faq-answer'>{entry.answer}</p>
          </div>
        )
      })
      faqContent = (
        <div id='faq'>
          <h2>Frequently Asked Questions</h2>
          {entries}
        </div>
      )
    }
    return (
      <div id='faq'>
        {faqContent}
      </div>
    )
  }
}

export default Faq

/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');

class Footer extends React.Component {
  render() {
    const currentYear = new Date().getFullYear();
    return (
      <footer className="nav-footer" id="footer">
        <section className="sitemap">
          <a href={this.props.config.baseUrl} className="nav-home">
            <img
              src={this.props.config.baseUrl + this.props.config.footerIcon}
              alt={this.props.config.title}
              width="66"
              height="58"
            />
          </a>
          <div>
            <h5>Background</h5>
            <a
              href={
                this.props.config.baseUrl +
                'docs' +
                '/intro.html'
              }>
              Introduction
            </a>
            <a
              href={
                this.props.config.baseUrl +
                'docs' +
                '/s3background.html'
              }>
              General S3 Background
            </a>
            <a
              href={
                this.props.config.baseUrl +
                'docs' +
                '/howitworks.html'
              }>
              How Bucket Snake Works
            </a>
          </div>
          <div>
            <h5>Getting Started</h5>
            <a
              href={
                this.props.config.baseUrl +
                'docs' +
                '/installation.html'
              }>
              Installation
            </a>
            <a
              href={
                this.props.config.baseUrl +
                'docs' +
                '/configuration.html'
              }>
              Configuration
            </a>
          </div>
          <div>
            <h5>Community</h5>
            <a
              href="https://github.com/Netflix-Skunkworks/bucketsnake">
              GitHub
            </a>
          </div>
        </section>

        <section className="copyright">
          These docs were created with <a href="https://docusaurus.io/">Docusaurus</a>.
        </section>

        <section className="copyright" style={{paddingTop: "10px"}}>
          Copyright &copy; {currentYear} Netflix, Inc.
        </section>
      </footer>
    );
  }
}

module.exports = Footer;

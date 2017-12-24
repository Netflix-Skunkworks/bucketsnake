/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');

const CompLibrary = require('../../core/CompLibrary.js');
const MarkdownBlock = CompLibrary.MarkdownBlock; /* Used to read markdown */
const Container = CompLibrary.Container;
const GridBlock = CompLibrary.GridBlock;

const siteConfig = require(process.cwd() + '/siteConfig.js');

class Button extends React.Component {
  render() {
    return (
      <div className="pluginWrapper buttonWrapper">
        <a className="button" href={this.props.href} target={this.props.target}>
          {this.props.children}
        </a>
      </div>
    );
  }
}

Button.defaultProps = {
  target: '_self',
};

class HomeSplash extends React.Component {
  render() {
    return (
      <div className="homeContainer">
        <div className="homeSplashFade">
          <div className="wrapper homeWrapper">
            <div className="inner">
              <h2 className="projectTitle">
                {siteConfig.title}
                <small>{siteConfig.tagline}</small>
                <img src={siteConfig.baseUrl + 'img/logo.png'} width="300px" />
                <small style={{color: "red"}}>**Bucket Snake is under heavy development and not yet ready for production usage.</small>
              </h2>
              <div className="section promoSection">
                <div className="promoRow">
                  <div className="pluginRowBlock">
                    <Button
                      href={
                        siteConfig.baseUrl +
                        'docs' +
                        '/intro.html'}>
                      Background Info</Button>
                    <Button
                      href={
                        siteConfig.baseUrl +
                        'docs' +
                        '/howitworks.html'}>
                      How it Works</Button>
                    <Button
                      href={
                        siteConfig.baseUrl +
                        'docs' +
                        '/installation.html'
                      }>
                      Getting Started
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

class Index extends React.Component {
  render() {
    let language = this.props.language || 'en';
    const showcase = siteConfig.users
      .filter(user => {
        return user.pinned;
      })
      .map(user => {
        return (
          <a href={user.infoLink}>
            <img src={user.image} title={user.caption} />
          </a>
        );
      });

    return (
      <div>
        <HomeSplash language={language} />
        <div className="mainContainer">
          <Container padding={['bottom', 'top']}>
            <GridBlock
              align="center"
              contents={[
                {
                  content: 'AWS Lambda function that does all the work.',
                  image: siteConfig.baseUrl + 'img/Compute_AWSLambda_LARGE.png',
                  imageAlign: 'top',
                  title: 'Serverless',
                },
                {
                  content: 'AWS S3 permissions are hard. Cross-account permissions are harder. Bucket Snake simplifies the provisioning of this.',
                  image: siteConfig.baseUrl + 'img/s3check.png',
                  imageAlign: 'top',
                  title: 'Simplify S3 Access',
                },
                {
                    content: 'Creates assumable roles in the bucket residing account. Applications assume these app-specific roles for S3 access.',
                    image: siteConfig.baseUrl + 'img/logo.png',
                    imageAlign: 'top',
                    title: 'Eliminate Cross-Account S3 Issues',
                },
              ]}
              layout="fourColumn"
            />
          </Container>

          <div
            className="productShowcaseSection paddingBottom"
            style={{textAlign: 'center'}}>
            <h2>Permanently resolve cross-account S3 access problems</h2>
            <MarkdownBlock>
              By relying on IAM for all S3 access, Bucket Snake resolves access issues by completely avoiding bucket and object ACLs.
            </MarkdownBlock>
          </div>

          <Container padding={['bottom', 'top']} background="light">
            <GridBlock
              contents={[
                {
                  content: 'Bucket Snake receives a JSON payload on lambda invocation with details on ' +
                  'which S3 buckets an application needs. Bucket Snake figures out the correct ' +
                  'IAM permissions to grant.\nThe application then has the correct permissions to assume into the ' +
                  'correct IAM roles to access a given bucket.\n\n' +
                  'See the [how it works](docs/howitworks.html) docs for details.',
                  image: siteConfig.baseUrl + 'img/logo.png',
                  imageAlign: 'right',
                  title: 'Granting the Right Permissions',
                },
              ]}
            />
          </Container>

        </div>
      </div>
    );
  }
}

module.exports = Index;

/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* List of projects/orgs using your project for the users page */
const users = [
  {
    caption: 'Bucket Snake',
    image: '/bucketsnake/img/logo.png',
    infoLink: 'https://github.com/Netflix-Skunkworks/bucketsnake',
    pinned: true,
  },
];

const siteConfig = {
  title: 'Bucket Snake' /* title for your website */,
  tagline: 'An AWS lambda function that grantsss S3 permissionsss at ssscale.',
  url: 'https://github.com/Netflix-Skunkworks/bucketsnake' /* your website url */,
  baseUrl: '/bucketsnake/' /* base url for your project */,
  projectName: 'bucketsnake',
  headerLinks: [
    {doc: 'intro', label: 'Docs'},
    {href: 'https://github.com/Netflix-Skunkworks/bucketsnake', label: 'GitHub'}
  ],
  users,
  /* path to images for header/footer */
  headerIcon: 'img/logo.png',
  footerIcon: 'img/logo.png',
  favicon: 'img/favicon.png',
  /* colors for website */
  colors: {
    /*primaryColor: '#ff8827',
    secondaryColor: '#ff6427',*/
    primaryColor: '#81d34c',
    secondaryColor: '#18421a'
  },
  // This copyright info is used in /core/Footer.js and blog rss/atom feeds.
  copyright:
    'Copyright © ' +
    new Date().getFullYear() +
    ' Netflix',
  organizationName: 'Netflix-Skunkworks', // or set an env variable ORGANIZATION_NAME
  projectName: 'bucketsnake', // or set an env variable PROJECT_NAME
  highlight: {
    // Highlight.js theme to use for syntax highlighting in code blocks
    theme: 'default',
  },
  scripts: ['https://buttons.github.io/buttons.js'],
  // You may provide arbitrary config keys to be used as needed by your template.
  repoUrl: 'https://github.com/facebook/test-site',
};

module.exports = siteConfig;

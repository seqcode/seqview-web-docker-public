# SeqView-Web Client

SeqView-Web is a file search wrapper around common genome browsers such as IGV and HiGlass. This project creates an embeddable javascript file for the application. This allows you to create your own backend to deal with API requests for file meta-data, files and calls to HiGlass.

## Installation

node >= 12.20.1

Clone the repo to your desired location and run:

```
npm install
```

## Building an embeddable Javascript File

In the repo, create config files .config.dev and .config.prod with the following information. Replace the fields with your desired fields:

```
{
    serverUrl: "http://localhost"
}
```

serverUrl is the URL the application will send API requests to.

To build an embeddable javascript file for production use:

```
npm run build
```

For development, you can make use of [React hot module replacement](https://github.com/gaearon/react-hot-loader) by running:

```
npm run start:dev
```

This will also start a development server to inform the website of any changes to the source code. The development server will be listening on a port that can be found in the configuration files. 

For both development and production, the built file can be found under dist/main.js. For an example of how to include this file with all its dependencies look at the file frontend/templates/frontend/index.html in the genome-browser repo.

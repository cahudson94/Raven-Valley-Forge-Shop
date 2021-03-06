# Raven-Valley-Forge-Shop
---
### Description
[![Build Status](https://travis-ci.org/cahudson94/Raven-Valley-Forge-Shop.svg?branch=master)](https://travis-ci.org/cahudson94/Raven-Valley-Forge-Shop) [![Coverage Status](https://coveralls.io/repos/github/cahudson94/Raven-Valley-Forge-Shop/badge.svg)](https://coveralls.io/github/cahudson94/Raven-Valley-Forge-Shop)

Version: 2.0.0

A Company and Store Site for Ravenmoore Valley Forge & Metalworks.
Built on Amazon AWS using Django 2, with Paypal, Google, EasyPost, and TaxJar API integrations.

### Authors
---
* [cahudson94](https://github.com/cahudson94/Raven-Valley-Forge-Shop)

### Dependencies
---
* generic
* discovery
* oauth2
* conf
* taxjar
* auth
* oauth2client
* paypalrestsdk
* managers
* paginator
* contrib
* http
* mixins
* uploadedfile
* fields
* django
* mail
* edit
* db
* s3boto3
* fields
* deletion
* decorators
* shortcuts
* easypost

### Getting Started
---
##### *Prerequisites*
* [python (3.6+)](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/)
* [git](https://git-scm.com/)

##### *Installation*
First, clone the project repo from Github. Then, change directories into the cloned repository. To accomplish this, execute these commands:

`$ git clone https://github.com/cahudson94/Raven-Valley-Forge-Shop.git`

`$ cd Raven-Valley-Forge-Shop`

Now now that you have cloned your repo and changed directories into the project, create a virtual environment named "ENV", and install the project requirements into your VE.

`$ python3 -m venv ENV`

`$ source ENV/bin/activate`

`$ pip install -r requirements.pip`

### Test Suite
---
##### *Running Tests*
This is a Django application, and therefore to run tests, run the following command at the same level as `./manage.py`.

`./manage.py test`
##### *Test Files*
The testing files for this project are:

| File Name | Description |
|:---:|:---:|
| `./RVFS/account/tests.py` | Test file for account views, models, urls, and forms. |
| `./RVFS/catalog/tests.py` | None |
| `./RVFS/RVFS/tests.py` | Test file for base html, main url/views, and google api calls. |

### Development Tools
---
* *python* - programming language

### License
---
This project is licensed under MIT License - see the LICENSE.md file for details.


*This README was generated using [writeme.](https://github.com/chelseadole/write-me)*

# Changelog for Thoth's Template GitHub Project

## [0.1.0] - 2019-Sep-11 - goern

### Added

all the things that you see...

## Release 0.2.0 (2020-05-15T16:53:59)
* Add environment info
* Add solvers info
* Add readme for testing locally
* Add TODO
* Add PyPI SLI
* Introduce base.html
* Add packages release Thoth
* New variable for user API
* Add user API and KNowledge Graph reports
* Adjust typing
* Update main file
* Add HTML templates
* Ad Jinja2
* Add environment variable
* Adjust sli for solved python packages
* Add SLI for learning rate
* Add SLI for workflows quality
* Add references that can be expanded
* Create main report class
* Create base class for all metrics to be reported
* refactor main file
* Add environment to distinguish metrics
* Use thanos secret
* updated the standard github templates
* Add reference dashboard
* Add version and folders
* Generalize email subject with week
* Use int type
* Correct docstrings
* Generalize metrics and reports
* Update main file
* Add some TODO
* Adjust app
* Add requirements

## Release 0.2.1 (2020-06-01T08:37:13)
* Add apiVersion
* :pushpin: Automatic update of dependency prometheus-client from 0.7.1 to 0.8.0
* :pencil: Readme fix
* updated zuul config file
* :art: Resolved suggested changes
* Remove int
* :pencil: Fixed readme
* :green_heart: Coala fix
* :sparkles: Added SLI report for Kebechet
* :pencil: Added readme for SLO Reporter
* :sparkles: some reformatting done by pre-commit
* :sparkles: added pre-commit config file
* Use index instead of knowledge graph
* Add PyPI info
* Change time
* Save HTML
* Add info for tables
* Add configuration
* Add style for report
* Adjust README
* Adjust report
* Proper dry run

## Release 0.3.0 (2020-06-16T15:51:48)
* Modify workflow query and introduce env variables
* :pushpin: Automatic update of dependency prometheus-api-client from 0.2.0 to 0.3.1
* Introduce error
* Correct docstring
* Add reference descriptions
* Add Thoth reports references

## Release 0.3.1 (2020-06-17T12:14:38)
* relock

## Release 0.4.0 (2020-06-24T13:36:35)
* Add min max only ascending order
* Missing sum
* Correct key
* Add env variable for learning rate
* Make sure we have a result even with holes in prometheus
* Move workflow to configuratin and aupdate README
* Add type of query range: min_max, latest, average
* Introduce latency
* Add env template
* Correct variable
* Correct verb
* make coala happy
* Add new variable
* Add docs on worklows
* Add requires_range variable
* Generalize time envs to be used
* Add query_range

## Release 0.5.0 (2020-07-03T11:28:34)
* Correct env variable
* Add delta action
* Make env optional with default to 1
* Update env variables
* Modify logic to allow multiple runs to collect previous data
* Add initilization to use same configuration for all reports
* Add initialization to the class for configuration
* Add method and standardize User API SLI
* Add method and standardize PyPI Knowledge Graph SLI
* Add method and standardize Thoth Learning SLI
* Add method and standardize Thoth Knowledge Graph SLI
* Add method and standardize Kebechet SLI
* Feature/standardize (#49)
* Update OWNERS
* Make pre-commit happy
* Change configuration to 1 day
* Add env variables to cronjob template
* Modify CronJob to run every day EOB
* Adjust files
* Add env variables and adjust dry run
* Add version of storages
* Add method to parse data and store on Ceph
* Add methods to store using CephStore
* Add env variables for store
* Add requirements for storages and process data
* Create OWNERS
* Change time

## Release 0.5.1 (2020-07-03T14:30:25)
* correct variable due to wrong rebase

## Release 0.5.2 (2020-07-08T10:59:36)
* Add day of week check to send emails (#56)

## Release 0.5.3 (2020-07-10T06:44:26)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.0 to 0.24.3 (#60)
* Adjust User-API SLI retrieve (#59)

## Release 0.5.4 (2020-08-24T08:54:11)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.5 to 0.25.5 (#72)
* Modify environment variable (#70)
* :pushpin: Automatic update of dependency pandas from 1.0.5 to 1.1.0 (#68)
* :pushpin: Automatic update of dependency pandas from 1.0.5 to 1.1.0 (#67)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.3 to 0.24.5 (#66)
* :pushpin: Automatic update of dependency thoth-storages from 0.24.3 to 0.24.5 (#65)
* :pushpin: Automatic update of dependency prometheus-api-client from 0.3.1 to 0.4.0 (#64)
* Add SLI for security workflow (#63)

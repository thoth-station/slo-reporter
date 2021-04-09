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

## Release 0.5.5 (2020-09-11T13:20:06)
### Features
* Update reference dashboard (#83)
### Automatic Updates
* :pushpin: Automatic update of dependency pandas from 1.1.1 to 1.1.2 (#86)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.5 to 0.25.7 (#85)
* :pushpin: Automatic update of dependency prometheus-api-client from 0.4.0 to 0.4.1 (#84)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#77)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#76)
* :pushpin: Automatic update of dependency pandas from 1.1.0 to 1.1.1 (#74)

## Release 0.5.6 (2020-09-21T07:03:17)
### Features
* Update evaluation method (#92)
### Automatic Updates
* :pushpin: Automatic update of dependency thoth-storages from 0.25.9 to 0.25.10 (#94)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.7 to 0.25.9 (#90)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.7 to 0.25.9 (#89)

## Release 0.5.7 (2020-09-24T10:17:17)
### Features
* Add SLI for Security-Indicator (#102)
* Explain metrics and SLI, add Images on SLI (#99)
* Add thoth integrations and introduce generalization for files stored in Ceph (#97)
### Improvements
* Adjust links to READMEs and images (#100)
### Other
* remove duplicate .png from link (#101)
### Automatic Updates
* :pushpin: Automatic update of dependency hypothesis from 5.35.4 to 5.36.0 (#107)
* :pushpin: Automatic update of dependency thoth-common from 0.19.0 to 0.20.0 (#106)
* :pushpin: Automatic update of dependency thoth-common from 0.19.0 to 0.20.0 (#105)
* :pushpin: Automatic update of dependency thoth-common from 0.19.0 to 0.20.0 (#104)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.10 to 0.25.11 (#98)

## Release 0.5.8 (2020-09-29T09:25:51)
### Features
* Add quality latency sli (#116)
### Automatic Updates
* :pushpin: Automatic update of dependency hypothesis from 5.36.0 to 5.36.1 (#114)
* :pushpin: Automatic update of dependency hypothesis from 5.36.0 to 5.36.1 (#113)
* :pushpin: Automatic update of dependency pytest from 6.0.2 to 6.1.0 (#112)
* :pushpin: Automatic update of dependency hypothesis from 5.35.4 to 5.36.0 (#111)
* :pushpin: Automatic update of dependency hypothesis from 5.35.4 to 5.36.0 (#110)

## Release 0.5.9 (2020-10-15T17:15:46)
### Features
* Add ‚change since last week‘ metrics (#130)
* reset time to utcnow (#132)
* Add sli columns check (#131)
### Automatic Updates
* :pushpin: Automatic update of dependency hypothesis from 5.37.1 to 5.37.3 (#140)
* :pushpin: Automatic update of dependency mypy from 0.782 to 0.790 (#137)
* :pushpin: Automatic update of dependency mypy from 0.782 to 0.790 (#136)
* :pushpin: Automatic update of dependency hypothesis from 5.37.0 to 5.37.1 (#135)
* :pushpin: Automatic update of dependency thoth-common from 0.20.0 to 0.20.1 (#134)
* :pushpin: Automatic update of dependency pandas from 1.1.2 to 1.1.3 (#133)
* :pushpin: Automatic update of dependency hypothesis from 5.36.1 to 5.37.0 (#129)
* :pushpin: Automatic update of dependency hypothesis from 5.36.1 to 5.37.0 (#128)
* :pushpin: Automatic update of dependency pytest from 6.1.0 to 6.1.1 (#127)
* :pushpin: Automatic update of dependency hypothesis from 5.36.1 to 5.37.0 (#126)
* :pushpin: Automatic update of dependency pytest from 6.1.0 to 6.1.1 (#125)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.14 to 0.25.15 (#124)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.13 to 0.25.14 (#123)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.12 to 0.25.13 (#121)
* :pushpin: Automatic update of dependency thoth-storages from 0.25.12 to 0.25.13 (#120)

## Release 0.6.0 (2020-10-22T16:21:22)
### Features
* check for DRY_RUN (#145)
* Adjust description (#144)
### Automatic Updates
* :pushpin: Automatic update of dependency thoth-common from 0.20.1 to 0.20.2 (#148)
* :pushpin: Automatic update of dependency thoth-common from 0.20.1 to 0.20.2 (#147)
* :pushpin: Automatic update of dependency hypothesis from 5.37.1 to 5.37.3 (#143)

## Release 0.6.1 (2020-10-23T07:23:45)
### Features
* Add environment to email title to avoid confusion (#154)
### Automatic Updates
* :pushpin: Automatic update of dependency hypothesis from 5.37.3 to 5.37.4 (#153)
* :pushpin: Automatic update of dependency hypothesis from 5.37.3 to 5.37.4 (#151)

## Release 0.7.0 (2020-11-26T11:49:13)
### Features
* Adjust metrics due to changes on Prometheus side (#164)
* Add check for Thanos availability before starting to acquire metrics. (#163)
* port to python 38 (#162)

## Release 0.8.0 (2021-01-21T09:57:37)
### Features
* :arrow_up: Automatic update of dependencies by kebechet. (#175)
* Adjust report provided in the email (#171)
* :arrow_up: Automatic update of dependencies by kebechet. (#173)
* added a sig label to be added to each PR
* reformatted by pre-commit
* :arrow_up: Automatic update of dependencies by kebechet. (#169)
* update .aicoe.yaml (#168)
### Improvements
* removed bissenbay, thanks for your contributions!
* :sparkles: more simplistic style

## Release 0.8.1 (2021-01-21T13:14:06)
### Features
* Change column name (#177)

## Release 0.8.2 (2021-01-28T07:30:25)
### Features
* Correct title email (#182)

## Release 0.8.3 (2021-02-02T08:42:58)
### Features
* :arrow_up: Automatic update of dependencies by kebechet. (#192)
* Introduce check on data retrieval from ceph (#190)
* :arrow_up: Automatic update of dependencies by kebechet. (#189)
* :arrow_up: Automatic update of dependencies by kebechet. (#187)

## Release 0.9.0 (2021-02-09T08:10:48)
### Features
* Feature/introduce sendgrid to send emails (#201)
* :arrow_up: Automatic update of dependencies by Kebechet (#199)

## Release 0.10.0 (2021-02-16T14:34:28)
### Features
* Generalize smtp tls (#206)
* :arrow_up: Automatic update of dependencies by Kebechet (#205)

## Release 0.11.0 (2021-03-11T08:40:39)
### Features
* :arrow_up: Automatic update of dependencies by Kebechet (#219)
*  Add integration per user SLI (#220)
* Add build analysis in the report (#214)
* :arrow_up: Automatic update of dependencies by Kebechet (#216)
* :arrow_up: update CI/CD configuration (#215)
* :arrow_up: Automatic update of dependencies by Kebechet (#212)
* :arrow_up: Automatic update of dependencies by Kebechet (#211)

## Release 0.11.1 (2021-03-19T11:55:29)
### Features
* Fix key for changes since last week
* :arrow_up: Automatic update of dependencies by Kebechet (#225)

## Release 0.12.0 (2021-03-19T17:41:35)
### Features
* Generalize references (#233)

## Release 0.13.0 (2021-03-29T12:17:32)
### Features
* :arrow_up: Automatic update of dependencies by Kebechet (#240)
* Add workflows tasks latency (#238)
* :arrow_up: Automatic update of dependencies by Kebechet (#237)
* :arrow_up: Automatic update of dependencies by Kebechet (#232)

## Release 0.13.1 (2021-04-09T15:09:50)
### Features
* Add defaults (#242)

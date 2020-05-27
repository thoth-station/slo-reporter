# Thoth Service Level Objective (SLO) reporter

This is Thoth SLO Reporter to share its achievements and behaviour with the outside world.

# Adding new SLI report
1. Add a class under [thoth/slo_reporter](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter) if it doesn't exist for the kind of report. This class would inherit the base class `SLIBase` from [sli_base.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/sli_base.py). 
2. Add a HTML jinja template that is to be included in the report here - [Link](https://github.com/thoth-station/slo-reporter/tree/master/thoth/slo_reporter/static/templates)
3. Add a method to load the template you designed in [sli_template.py](https://github.com/thoth-station/slo-reporter/blob/master/thoth/slo_reporter/sli_template.py) and add a method to take in the populate the template. 
4. The query method can be tested agnaist the Prometheus web UI before being added to the method here - [Link](https://prometheus-dh-prod-monitoring.cloud.datahub.psi.redhat.com/graph)
5. In the class that you created in step 1, add a `aggregate_info` method to return the query and the report.
```python    
def _aggregate_info(self):
    """"Aggregate info required for knowledge graph SLI Report."""
    return {"query": self._query_sli(), "report_method": self._report_sli}
```
6. The report can be tested using the command stated below. 

### Testing (dry run)

The following command will open a web browser showing how the report will look like.

```python
DEBUG_LEVEL=1 DRY_RUN=1 pipenv run python3 app.py
```
# Thoth Learning

## SLILearning

Thoth Learning SLI shows all Thoth information related to learning rates and amount of knowledge learned:

- `solvers` considers the number of [solvers](https://github.com/thoth-station/thoth-application/blob/e6eaa6b189bae46092877624fe38abf9850f5484/core/base/configmaps.yaml#L14) currently considered by Thoth.

```yaml
data:
  solvers: |
    solver-rhel-8-py36
    solver-fedora-31-py38
    solver-fedora-31-py37
    solver-fedora-32-py37
    solver-fedora-32-py38
```

Solvers collect knowledge using [Thoth Dependency Solver](https://github.com/thoth-station/solver) which tries to answer a simple question:
what packages will be installed (resolved by pip or any Python compliant dependency resolver) for the provided stack?

- `new_solvers` considers the changes in the number of solvers respect to the period considered in SLO reporter when run.

- `average_solver_learning_rate` is related to solved packages. How fast are we learning (solving) packages in a certain period of time.

`_LEARNING_RATE_INTERVAL` considers the interval used to evaluate the learning rate.
Considering the period of evaluation of SLI reporter, e.g. 1 day, the average learning rate
is evaluated considering the average of the learning rates evaluated over a window of two hours in 1 day period.

For example if the average learning rate is 100 -> learning rate is 1000 packages solved in 1h, or equivalently ~17 packages solved per minute.

This value is customizable, each time might want to focus on longer periods (e.g. weekly or quarterly)

- `solved_packages` this value is directly linked to the learning rate of solved packages. It shows the number of packages learned in the period of evaluation
for SLO reporter, typically per day.

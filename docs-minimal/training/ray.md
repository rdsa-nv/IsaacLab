# Ray Integration

**Use Ray for hyperparameter tuning and distributed job management with Isaac Lab.**

## Overview

[Ray Tune](https://docs.ray.io/en/latest/tune/index.html) integrates with Isaac Lab for:

- **Hyperparameter search**: Grid, random, Bayesian, population-based
- **Distributed experiments**: Run multiple training jobs across GPUs
- **Experiment tracking**: Automatic logging and comparison

## Setup

```bash
pip install ray[tune]
```

## Hyperparameter tuning

```python
from ray import tune
from ray.tune.schedulers import ASHAScheduler

# Define search space
config = {
    "learning_rate": tune.loguniform(1e-5, 1e-2),
    "gamma": tune.uniform(0.95, 0.999),
    "entropy_coef": tune.loguniform(1e-4, 1e-1),
    "num_steps_per_env": tune.choice([16, 24, 32, 48]),
    "hidden_dims": tune.choice([[256, 256], [512, 256], [512, 512]]),
}

# Early stopping scheduler
scheduler = ASHAScheduler(
    metric="mean_reward",
    mode="max",
    max_t=5000,          # Max training iterations
    grace_period=500,    # Min iterations before stopping
    reduction_factor=3,
)
```

## Running a tuning job

```bash
./isaaclab.sh -p scripts/reinforcement_learning/ray/tune.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_samples 20 \
    --num_gpus_per_trial 1
```

Key arguments:

| Argument | Description |
|----------|-------------|
| `--num_samples` | Total number of hyperparameter combinations to try |
| `--num_gpus_per_trial` | GPUs allocated per trial |
| `--max_concurrent_trials` | Parallel trials (limited by GPU count) |
| `--scheduler` | `asha`, `pbt`, `median` |

## Distributed job dispatch

Ray can distribute independent training runs across multiple GPUs:

```python
from ray import tune

# Run 8 seeds of the same config
tune.run(
    train_fn,
    config={"seed": tune.grid_search([0, 1, 2, 3, 4, 5, 6, 7])},
    resources_per_trial={"gpu": 1},
)
```

## Analyzing results

```python
from ray.tune import ExperimentAnalysis

analysis = ExperimentAnalysis("~/ray_results/my_experiment")

# Best config
best = analysis.get_best_config(metric="mean_reward", mode="max")
print(f"Best learning rate: {best['learning_rate']}")

# Results dataframe
df = analysis.dataframe()
```

## Integration with RL frameworks

Ray Tune wraps around any Isaac Lab training script. The training function receives a config dict and reports metrics:

```python
def train_fn(config):
    # Override RL config with Ray's sampled values
    runner_cfg.algorithm.learning_rate = config["learning_rate"]
    runner_cfg.algorithm.gamma = config["gamma"]

    # Train
    runner = OnPolicyRunner(env, runner_cfg)
    for epoch in range(runner_cfg.max_iterations):
        metrics = runner.train_step()
        tune.report(mean_reward=metrics["mean_reward"])
```

## Tips

- **Start with random search** (10-20 samples) to find the right order of magnitude for each parameter.
- **Use ASHA scheduler** to early-stop bad trials — saves significant GPU time.
- **Tune one thing at a time**: First find a good learning rate, then tune other parameters.
- **Log to WandB**: Ray Tune integrates with Weights & Biases for experiment tracking.
- **Resource planning**: With 4 GPUs and `num_gpus_per_trial=1`, you get 4 concurrent trials.

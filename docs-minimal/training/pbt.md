# Population-Based Training

**Automatically tune hyperparameters during training by evolving a population of agents.**

## Overview

Population-Based Training (PBT) runs multiple agents simultaneously, periodically replacing underperforming agents with mutated copies of top performers. Unlike grid search, PBT adapts hyperparameters *during* training.

!!! note
    PBT is currently supported with **RL Games** only.

## How PBT works

1. **Initialize**: Launch N agents with different random hyperparameters
2. **Train**: Each agent trains independently for an interval
3. **Evaluate**: Rank agents by reward
4. **Exploit**: Replace bottom performers with copies of top performers
5. **Explore**: Mutate the copied hyperparameters (perturb or resample)
6. **Repeat** from step 2

## Configuration

```python
from isaaclab.utils.pbt import PBTCfg

pbt_cfg = PBTCfg(
    population_size=8,              # Number of agents
    interval=100,                   # Steps between exploit/explore
    metric="mean_reward",           # Metric to optimize
    mode="max",                     # Maximize metric
    selection="leader",             # Selection strategy
    mutation_fraction=0.25,         # Fraction of params to mutate
    perturbation_factor=0.2,        # Perturbation range (+/- 20%)
    hyperparameters={
        "learning_rate": {
            "type": "loguniform",
            "range": [1e-5, 1e-2],
        },
        "entropy_coef": {
            "type": "loguniform",
            "range": [1e-4, 1e-1],
        },
        "gamma": {
            "type": "uniform",
            "range": [0.95, 0.999],
        },
    },
)
```

## Running PBT

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train_pbt.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --population_size 8 \
    --num_envs 1024 \
    --headless
```

Each agent in the population uses `num_envs / population_size` environments.

## Selection strategies

| Strategy | How it works |
|----------|-------------|
| `"leader"` | Bottom agents copy the single best agent |
| `"truncation"` | Bottom 20% copies from top 20% |
| `"binary_tournament"` | Pairwise comparison, loser copies winner |

## GPU requirements

PBT multiplies GPU memory usage by the population size. Plan accordingly:

| Population | Envs per agent | Total envs | Approx. VRAM |
|-----------|---------------|------------|---------------|
| 4 | 1024 | 4096 | ~16 GB |
| 8 | 512 | 4096 | ~16 GB |
| 8 | 1024 | 8192 | ~32 GB |
| 16 | 512 | 8192 | ~32 GB |

## Tips

- **Start with population_size=4-8** — larger populations find better parameters but cost more GPU memory.
- **Set interval carefully**: Too short = not enough training between evaluations. Too long = slow adaptation. 100-500 steps is typical.
- **PBT vs Ray Tune**: PBT adapts during training (good for schedule-sensitive parameters like learning rate). Ray Tune explores independent configurations (good for architecture choices).
- **Monitor the population**: Track which agents get replaced and what parameters converge to.

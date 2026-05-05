# HPC Deployment

**Run Isaac Lab on SLURM clusters and HPC systems.**

## SLURM job script

```bash
#!/bin/bash
#SBATCH --job-name=isaac-lab-train
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --partition=gpu

# Load modules (cluster-specific)
module load cuda/12.2
module load singularity

# Run with Singularity container
singularity exec --nv \
    isaac-lab.sif \
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
        --task Isaac-Velocity-Flat-Anymal-C-v0 \
        --num_envs 4096 \
        --headless
```

Submit:

```bash
sbatch train_job.sh
```

## Multi-GPU on SLURM

```bash
#!/bin/bash
#SBATCH --gpus-per-node=4

singularity exec --nv isaac-lab.sif \
    torchrun --nnodes=1 --nproc_per_node=4 \
    scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_envs 4096 --distributed --headless
```

## Multi-node training

```bash
#!/bin/bash
#SBATCH --nodes=2
#SBATCH --gpus-per-node=4
#SBATCH --ntasks-per-node=4

srun singularity exec --nv isaac-lab.sif \
    torchrun \
    --nnodes=$SLURM_NNODES \
    --nproc_per_node=4 \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$MASTER_ADDR:$MASTER_PORT \
    scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_envs 8192 --distributed --headless
```

## Singularity / Apptainer

Most HPC clusters use Singularity instead of Docker:

```bash
# Convert Docker image to Singularity
singularity build isaac-lab.sif docker://nvcr.io/nvidia/isaac-lab:latest

# Run
singularity exec --nv isaac-lab.sif ./isaaclab.sh -p train.py --task MyTask --headless
```

Key flags:

| Flag | Purpose |
|------|---------|
| `--nv` | Enable NVIDIA GPU support |
| `--bind /scratch:/scratch` | Mount scratch storage |
| `--cleanenv` | Clean environment (recommended) |

## PBS / Torque

```bash
#!/bin/bash
#PBS -N isaac-lab-train
#PBS -l select=1:ngpus=4:ncpus=32
#PBS -l walltime=24:00:00
#PBS -q gpu

cd $PBS_O_WORKDIR

singularity exec --nv isaac-lab.sif \
    ./isaaclab.sh -p train.py --task MyTask --num_envs 4096 --headless
```

## Hyperparameter sweeps on HPC

Use SLURM job arrays for parallel hyperparameter search:

```bash
#!/bin/bash
#SBATCH --array=0-7
#SBATCH --gpus-per-node=1

SEEDS=(42 123 456 789 1024 2048 4096 8192)
SEED=${SEEDS[$SLURM_ARRAY_TASK_ID]}

singularity exec --nv isaac-lab.sif \
    ./isaaclab.sh -p train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --seed $SEED --headless
```

## Tips

- **Use `--headless` always** — HPC nodes typically have no display.
- **Mount fast storage** (NVMe/SSD) for log output — network filesystems slow down checkpoint saving.
- **Request enough CPU memory**: Isaac Lab's physics engine uses significant host memory for large env counts.
- **Check GPU driver version**: Ensure the container's CUDA is compatible with the cluster's driver.
- **Use job arrays** for seed sweeps instead of launching jobs manually.

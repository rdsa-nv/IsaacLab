# Record Videos

**Capture rollout videos for evaluation, papers, and debugging.**

## During evaluation

The simplest way: use the `--video` flag with the play/eval scripts:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_envs 1 \
    --video \
    --video_length 300 \
    --checkpoint logs/rsl_rl/anymal_c_flat/model_5000.pt
```

Videos are saved to the log directory as MP4 files.

## During training

Log periodic videos to TensorBoard/WandB:

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-C-v0 \
    --num_envs 4096 \
    --video \
    --video_length 200 \
    --video_interval 5000    # Every 5000 steps
```

## Using Gymnasium wrappers

Isaac Lab environments support the standard Gymnasium `RecordVideo` wrapper:

```python
import gymnasium as gym
from gymnasium.wrappers import RecordVideo

env = gym.make("Isaac-Velocity-Flat-Anymal-C-v0", num_envs=1, enable_cameras=True)
env = RecordVideo(env, video_folder="./videos", episode_trigger=lambda x: x % 10 == 0)

obs, info = env.reset()
for _ in range(1000):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()
```

## Camera placement

For good evaluation videos, configure a dedicated viewport camera:

```python
from isaaclab.sensors import CameraCfg

viewport_cam = CameraCfg(
    prim_path="/World/ViewportCam",
    height=720,
    width=1280,
    data_types=["rgb"],
    offset=CameraCfg.OffsetCfg(
        pos=[3.0, 3.0, 2.0],   # Positioned for a good view
        rot=[0.38, 0.14, -0.33, 0.85],
    ),
)
```

## Tips

- **Use `--num_envs 1`** for clean videos (multiple envs clutter the frame).
- **Enable `--enable_cameras`** when recording — cameras are off by default for performance.
- **Headless recording** works: `--headless --video` renders offscreen.
- **Video format**: Output is MP4 with H.264 encoding. Adjust `video_length` (in steps) to control duration.
- **For papers**: Use a fixed camera angle and consistent lighting. Record multiple seeds for representative results.

"""Independent public-only MiniGrid step/reset interface witness; no Yggdrasil training."""
import hashlib
import json
import platform
import time

import gymnasium as gym
import gymnasium as gymnasium
import minigrid
import numpy as np

ENV = "MiniGrid-Empty-5x5-v0"
ACTIONS = (0, 1, 2, 2, 2, 2, 2)


def public_receipt(observation):
    assert type(observation) is dict
    assert "image" in observation and "direction" in observation and "mission" in observation
    image = observation["image"]
    assert isinstance(image, np.ndarray) and image.ndim == 3
    assert np.issubdtype(image.dtype, np.integer)
    direction = int(observation["direction"])
    assert 0 <= direction <= 3
    assert isinstance(observation["mission"], str)
    return {
        "image_shape": list(image.shape),
        "image_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
        "direction": direction,
        "public_mission_sha256": hashlib.sha256(observation["mission"].encode()).hexdigest()
    }


def main():
    assert gymnasium.__version__ == "1.2.1", gymnasium.__version__
    assert minigrid.__version__ == "3.0.0", minigrid.__version__
    env = gym.make(ENV)
    try:
        start_wall = time.perf_counter_ns()
        start_cpu = time.process_time_ns()
        obs, _public_info = env.reset(seed=11)
        records = [{"step": 0, "observation": public_receipt(obs)}]
        done = False
        for n, action in enumerate(ACTIONS, 1):
            assert env.action_space.contains(action)
            obs, reward, terminated, truncated, _public_info = env.step(action)
            assert type(terminated) is bool and type(truncated) is bool
            assert isinstance(reward, (float, int)) and np.isfinite(reward)
            done = terminated or truncated
            records.append({"step": n, "action_id": action, "reward": float(reward),
                            "terminated": terminated, "truncated": truncated,
                            "observation": public_receipt(obs)})
            if done:
                break
        result = {
            "schema": "itd02.v31x.authentic_public_interface.v1",
            "classification": "V31X_AUTHENTIC_PUBLIC_INTERFACE_ONLY__NO_SCIENCE",
            "environment": ENV, "seed": 11,
            "gymnasium_version": gymnasium.__version__,
            "minigrid_version": minigrid.__version__,
            "python": platform.python_version(),
            "system": platform.system(),
            "steps": len(records)-1, "completed": done,
            "wall_ns": time.perf_counter_ns()-start_wall,
            "process_cpu_ns": time.process_time_ns()-start_cpu,
            "records": records, "learning_performed": False,
            "heldout_evaluated": False, "scientific_first_use": False
        }
        assert result["steps"] > 0
        print(json.dumps(result, sort_keys=True))
    finally:
        env.close()


if __name__ == "__main__":
    main()

import random
from pathlib import Path

import numpy as np
from collections import OrderedDict
from typing import List

from frame_comparison_tool.utils import FrameLoader


class Model:
    def __init__(self, n_samples: int = 5):
        self.sources: OrderedDict[str, FrameLoader] = OrderedDict()
        self.n_samples: int = n_samples
        self.curr_src_idx: int = 0
        self.curr_frame_idx: int = 0
        self._frame_ids: List[int] = []

    @property
    def frame_ids(self) -> List[int]:
        return self._frame_ids

    def _sample_frame_ids(self) -> None:
        random.seed(42)
        min_total_frames = min([source.total_frames for source in self.sources.values()])
        self._frame_ids = sorted([random.randint(0, min_total_frames) for _ in range(self.n_samples)])

        for source in self.sources.values():
            source.sample_frames(self._frame_ids)

    def add_source(self, file_path: Path) -> bool:
        file_path_str = str(file_path.absolute())

        if file_path_str in self.sources:
            return False
        else:
            frame_loader = FrameLoader(Path(file_path))
            self.sources[file_path_str] = frame_loader
            self._sample_frame_ids()
            return True

    def get_current_source(self) -> FrameLoader:
        return list(self.sources.values())[self.curr_src_idx]

    def get_current_frame(self) -> np.ndarray:
        return self.get_current_source().frames[self.curr_frame_idx]
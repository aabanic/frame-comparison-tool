from typing import Tuple

import numpy as np

from frame_comparison_tool.model import Model
from frame_comparison_tool.view import View, ViewData, DisplayMode
from PIL import Image


class Presenter:
    def __init__(self, model: Model, view: View):
        self.model: Model = model
        self.view: View = view
        self.view.set_presenter(self)
        self._connect_signals()
        self._set_initial_frame_size()

    def _set_initial_frame_size(self) -> None:
        initial_frame_size = self.view.get_max_frame_size()
        self.set_max_frame_size(max_frame_size=initial_frame_size)

    def _connect_signals(self) -> None:
        self.view.add_source_requested.connect(self.add_source)
        self.view.delete_source_requested.connect(self.delete_source)
        self.view.mode_changed.connect(self.change_mode)
        self.view.frame_changed.connect(self.change_frame)
        self.view.source_changed.connect(self.change_source)
        self.view.resize_requested.connect(self.resize_frame)

    def add_source(self, file_path: str) -> None:
        if self.model.add_source(file_path):
            self.view.on_add_source(file_path)
            self.update_display()

    def delete_source(self, file_path: str) -> None:
        idx = self.model.delete_source(file_path)
        self.view.on_delete_source(idx)
        self.update_display()

    def change_frame(self, direction: int) -> None:
        self.model.curr_frame_idx += direction
        self.model.curr_frame_idx = max(0, min(self.model.curr_frame_idx, len(self.model.frame_ids) - 1))
        self.update_display()

    def change_source(self, direction: int) -> None:
        self.model.curr_src_idx += direction
        self.model.curr_src_idx = max(0, min(self.model.curr_src_idx, len(self.model.sources) - 1))
        self.update_display()

    def change_mode(self, mode: DisplayMode) -> None:
        if mode != self.model.curr_mode:
            self.model.curr_mode = mode
            self.update_display()

    def resize_frame(self, frame_size: Tuple[int, int]) -> None:
        if frame_size != self.model.max_frame_size:
            self.set_max_frame_size(max_frame_size=frame_size)
            self.update_display()

    def set_max_frame_size(self, max_frame_size: Tuple[int, int]) -> None:
        self.model.max_frame_size = max_frame_size

    def update_display(self) -> None:
        mode: DisplayMode = self.model.curr_mode
        view_data: ViewData

        if len(self.model.sources) == 0:
            view_data = ViewData(frame=None, mode=mode)
        else:
            frame = self.model.get_current_frame()

            if mode == DisplayMode.SCALED:
                frame = self._resize_frame_to_fit(frame)

            view_data = ViewData(frame=frame, mode=mode)

        self.view.update_display(view_data)

    def _resize_frame_to_fit(self, frame: np.ndarray) -> np.ndarray:
        max_frame_size: Tuple[int, int] = self.model.max_frame_size

        if max_frame_size[0] == 0 or max_frame_size[1] == 0:
            raise ValueError("Width or height cannot be zero.")

        image = Image.fromarray(frame)
        image.thumbnail(max_frame_size)
        return np.array(image)

"""
Primary Bed class.

@Author: Ryan Wall (2025)
"""

from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from dataclasses import dataclass, field
import copy
from pygarden._color_data import COLORDICT
import numpy as np

@dataclass
class Bed:
    """
    This is the primary class for making garden beds. It can contain children
    which will be aligned relative to the parent bed's position.

    This uses the matplotlib library and conventions to define the position
    and size
    """

    width: float = None
    height: float = None
    x: float = 0
    y: float = 0
    color: list = None
    children: list = field(default_factory=list)
    parent: Bed = None
    label: str = None
    # _angle: float = 0

    def __post_init__(self):
        self._width = self.width

    @property
    def absolute_x(self):
        outx = self.x
        if self.parent is not None:
            outx = outx + self.parent.absolute_x

        return outx

    @property
    def absolute_y(self):
        outy = self.y
        if self.parent is not None:
            outy = outy + self.parent.absolute_y

        return outy

    @property
    def get_rectangle(self):
        rect_self = Rectangle(
            (self.absolute_x, self.absolute_y),
            width=self.width,
            height=self.height,
            facecolor=self.color,
            # angle=self._angle,
            # rotation_point="center",
            edgecolor=COLORDICT["edgecolor"],
        )
        return rect_self

    @property
    def width(self):
        """If the width isn't set, pull from parent"""
        if isinstance(self._width, property):
            # Having a hard time with the default value, this incarnates it
            self._width = None
        if (self._width is None) and (self.parent is not None):
            return self.parent.width
        else:
            return self._width

    @width.setter
    def width(self, value: float):
        self._width = value

    @property
    def height(self):
        """If the height isn't set, pull from parent"""
        if isinstance(self._height, property):
            # Having a hard time with the default value, this incarnates it
            self._height = None
        if (self._height is None) and (self.parent is not None):
            return self.parent.height
        else:
            return self._height

    @height.setter
    def height(self, value: float):
        self._height = value

    @property
    def color(self):
        """If the color isn't set, pass None to matplotlib"""
        if isinstance(self._color, property):
            # Having a hard time with the default value, this incarnates it
            self._color = None
        return self._color

    @color.setter
    def color(self, c: list[float] | str):
        """Set colors compatible with matplotlib. There are some premade
        special values specified in pygarden._color_data:
            "path"
            "bed"
            "tomatoes"
            "veggies"
            "vegetables"
            "veg"
        """
        # For known colors
        if isinstance(c, str) and (c.lower() in COLORDICT.keys()):
            c = COLORDICT[c.lower()]
        self._color = c

    def add_children(self, beds: Bed | list[Bed]):
        if isinstance(beds, list):
            for bed in beds:
                self.add_children(bed)
        else:
            bed = beds
            bed.parent = self
            self.children.append(bed)

    def add_text(self, ax: plt.axis):
        if self.label is not None:
            textpos_x = self.absolute_x + self.width / 2
            textpos_y = self.absolute_y + self.height / 2
            ax.text(
                textpos_x,
                textpos_y,
                self.label,
                ha="center",
                va="center",
                color=COLORDICT["textcolor"],
            )

    def render_on_axis(self, ax: plt.axis):
        ax.add_patch(self.get_rectangle)
        self.add_text(ax)
        if self.children is not None:
            for child in self.children:
                child.render_on_axis(ax)

    def render(self):
        if self.parent is not None:
            f, ax = self.parent.render()
        else:
            f, ax = plt.subplots()
            self.render_on_axis(ax)
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)

            ax.set_yticks([])
            ax.set_xticks([])

            fig_width = 6
            fig_height = fig_width * (self.height / self.width)
            f.set_size_inches(fig_width, fig_height)
        return f, ax

    def copy(self) -> Bed:
        """Return a deep copy of the object"""
        return copy.deepcopy(self)

    def mirror_vertically(self) -> Bed:
        """Reverse the order of the objects in the Bed"""
        # Only does anything to self if there is a parent
        if self.parent is not None:
            parent_height = self.parent.height
            y_new = parent_height - self.height - self.y
            self.y = y_new
        for child in self.children:
            if child is not None:
                child.mirror_vertically()

        return self

    def mirror_horizontally(self) -> Bed:
        """Mirror the beds horizontally"""
        # Only does anything to self if there is a parent
        if self.parent is not None:
            parent_width = self.parent.width
            x_new = parent_width - self.width - self.x
            self.x = x_new
        for child in self.children:
            if child is not None:
                child.mirror_horizontally()

        return self

    # @property
    # def perceived_x(self) -> float:
    #     """Given some angle what is the perceived X"""

    #     rad_angle = np.deg2rad(self._angle)
    #     new_x = self.absolute_x*np.cos(rad_angle) + self.absolute_y*np.sin(rad_angle)
    #     return new_x
    
    # @property
    # def perceived_y(self) -> float:
    #     """Given some angle what is the perceived X"""

    #     rad_angle = np.deg2rad(self._angle)
    #     new_y = self.absolute_x*np.sin(rad_angle) + self.absolute_y*np.cos(rad_angle)
    #     return new_y


    def pivot(self, angle: float = 90) -> Bed:
        """Rotate by some amount"""
        self.x = old_y
        self.y = old_x
        # Do the hidden dimensions to keep the None effects of self.width and
        # self.height the same
        self._width = old_h
        self._height = old_w
        # self._angle += angle
        for child in self.children:
            if child is not None:
                child.pivot(angle)

        return self

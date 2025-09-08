#  MIT License
#
#  Copyright (c) 2025 [fullname]
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.

from BudapestMetroDisplay.model import RGB

#  Color helper functions


def _clamp8(x: int) -> int:
    """Clamp integer 'x' into the valid DMX byte range [0..255]."""
    return 0 if x < 0 else min(x, 255)


def _rgb_clamp(rgb: RGB) -> RGB:
    """Apply 8-bit clamping to all channels in an RGB triple."""
    return _clamp8(rgb[0]), _clamp8(rgb[1]), _clamp8(rgb[2])  # channel-wise clamp


def _rgb_max(a: RGB, b: RGB) -> RGB:
    """Channel-wise maximum (your 'brightest wins' blend)."""
    return max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2])


def _rgb_scale(rgb: RGB, factor: float) -> RGB:
    """Multiply each channel by 'factor' (used to dim defaults when idle)."""
    return (
        _clamp8(int(rgb[0] * factor)),
        _clamp8(int(rgb[1] * factor)),
        _clamp8(int(rgb[2] * factor)),
    )


#  Easing - interpolation


def ease_linear(t: float) -> float:
    """Linear easing: input progress t∈[0,1] → t."""
    return t  # no curve, straight interpolation


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease: slow-in, fast mid, slow-out; pleasant for fades."""
    return (
        2 * t * t if t < 0.5 else 1 - ((-2 * t + 2) ** 2) / 2
    )  # standard in/out quad curve

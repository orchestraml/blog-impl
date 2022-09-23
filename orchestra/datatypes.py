from typing import (
    Literal,
)

# TODO: Do we need a data type for Array or List?


class DataType:
    """
    Parent class of all data types.
    Throws an error if used directly.
    """

    human_readable = Literal[True, False]
    """
    human_readable must be set by the user unless pre-set by a child class
    """
    model_readable = Literal[True, False]
    """
    human_readable must be set by the user unless pre-set by a child class
    """


class String(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ❌
    """

    human_readable = Literal[True]
    model_readable = Literal[False]


class Boolean(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ❌
    """

    human_readable = Literal[True]
    model_readable = Literal[False]


class Timestamp(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ❌
    """

    human_readable = Literal[True]
    model_readable = Literal[False]


class ImageFile(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ❌
    """

    human_readable = Literal[True]
    model_readable = Literal[False]


class AudioFile(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ❌
    """

    human_readable = Literal[True]
    model_readable = Literal[False]


class FloatVector(DataType):
    """
    Human-readable(DataType): ❌
    Model-readable(DataType): ✅
    """

    human_readable = Literal[False]
    model_readable = Literal[True]

    length: int
    """
    Number of floats that make up this embedding
    e.g., [0.4, 0.4, 0.5] == 3
    """


class DoubleVector(DataType):
    """
    Human-readable(DataType): ❌
    Model-readable(DataType): ✅
    """

    human_readable = Literal[False]
    model_readable = Literal[True]

    length: int
    """
    Number of floats that make up this embedding
    e.g., [0.4, 0.4, 0.5] == 3
    """


class Int64(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ✅
    """


class Int32(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ✅
    """


class Float(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ✅
    """


class Double(DataType):
    """
    Human-readable(DataType): ✅
    Model-readable(DataType): ✅
    """

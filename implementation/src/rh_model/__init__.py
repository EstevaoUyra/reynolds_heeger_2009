"""Reynolds & Heeger (2009) Normalization Model of Attention.

Implementation follows article_aware/spec/model_spec.yaml.
"""

from .model import (
    ModelParams,
    build_attention_field,
    build_stimulus_drive,
    build_suppressive_kernel,
    compute_output,
    compute_suppressive_drive,
    default_params,
    simulate,
)
from . import protocols, helpers

__all__ = [
    "ModelParams",
    "build_attention_field",
    "build_stimulus_drive",
    "build_suppressive_kernel",
    "compute_output",
    "compute_suppressive_drive",
    "default_params",
    "simulate",
    "protocols",
    "helpers",
]

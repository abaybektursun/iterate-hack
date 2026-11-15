"""The one place the basins GPU jobs set vLLM's environment. Call enter() before importing vllm.

The Modal image has no nvcc, so every kernel vLLM would JIT-compile is turned off: the FlashInfer sampler (via the
team's ENGINE_ENV; job frustea-1114-152501-615c) and DeepGEMM for FP8 models (job frustea-1114-153448-dce3).
"""
import os


def enter():
    from studies.rlneurons.lib.n13_gen import ENGINE_ENV
    os.environ.update(ENGINE_ENV)
    os.environ["VLLM_USE_DEEP_GEMM"] = "0"

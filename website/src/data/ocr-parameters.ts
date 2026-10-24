import type { ParameterCount } from '../lib/ocr-pareto';

// Architecture-derived estimates, reviewed 2026-10-24 using Transformers 5.15.0.
// Shared parameters are counted once. Active counts exclude nn.Embedding tables
// and Gemma's audio-only modules. Vision encoders and projectors are included.
// Source configs are pinned below; the counting recipe is in methodology/#model-size.
const count = (total: number, active: number, revision: string): ParameterCount => ({ total, active, revision });
export const modelParameters: Record<string, ParameterCount> = {
  'Riksarkivet/trocr-base-handwritten-hist-swe-2': count(384864768, 333393408, 'aa79fcb1850bf3155ebc442570d6c6bfc0ac8100'),
  'Sprakbanken/TrOCR-norhand-v3': count(333921792, 281924096, 'd22eebb5312ac5190b1b1744c5727faa0d3f353d'),
  'stepfun-ai/GOT-OCR-2.0-hf': count(560528640, 405024000, 'd3017ef2c2c1395888c8d635c5e0508bcb0ac78d'),
  'zai-org/GLM-OCR': count(1107405824, 1016179712, '2e85a62840ccac27daa451df36c736c4636b8628'),
  'PaddlePaddle/PaddleOCR-VL-1.6': count(905601648, 798855664, 'c5630abae1d940eafe0697512a0325494b02ab42'),
  'Qwen/Qwen2-VL-2B-Instruct': count(2208985600, 1975611904, '895c3a49bc3fa70a340399125c650a463535e71c'),
  'Qwen/Qwen2-VL-7B-Instruct': count(8291375616, 7746378240, 'eed13092ef92e448dd6875b2a00151bd3f7db0ac'),
  'Qwen/Qwen3-VL-2B-Instruct': count(2127532032, 1814007808, '89644892e4d85e24eaac8bacfd4f463576704203'),
  'Qwen/Qwen3-VL-4B-Instruct': count(4437815808, 4046500352, 'ebb281ec70b05090aa6165b016eac8ec08e71b17'),
  'HuggingFaceTB/SmolVLM2-2.2B-Instruct': count(2246784880, 2145019632, '482adb537c021c86670beed01cd58990d01e72e4'),
  'google/gemma-4-E2B-it': count(5104297504, 2045650176, '3e22461f65e89153144f8adb70e3b8c2cc9845a7'),
  'google/gemma-4-E4B-it': count(7941100832, 4142683136, 'ee0ef6023621cff504d758262d4e04895a5af4a2'),
  'google/gemma-3-4b-it': count(4300079472, 3624108400, '093f9f388b31de276ce2de164bdc2081324b9767'),
  'Qwen/Qwen3.5-2B': count(2213241664, 1702323008, '15852e8c16360a2fea060d615a32b45270f8a8fc'),
  'Qwen/Qwen3.5-4B': count(4539265536, 3901207040, '851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a'),
  'datalab-to/chandra-ocr-2': count(4539265536, 3901207040, 'af93b47dba1b47b6640c86ccf487ed2260ab9a09'),
};

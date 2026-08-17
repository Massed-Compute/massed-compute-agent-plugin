---
name: mc-pick-gpu
description: Use when the user is choosing a GPU instance type on Massed Compute, deciding which Massed Compute SKU to launch, or asking which GPU fits a workload (LLM inference, fine-tuning, diffusion, training, HPC). Probes the user for the workload details that meaningfully change the answer, then presents two or three ranked candidates from Massed Compute's specific inventory with tradeoffs.
type: skill
---

# mc-pick-gpu

## When to use this skill

Trigger when the user is in the SKU-selection phase on Massed Compute: "which GPU for Llama 70B?", "cheapest card that fits Flux?", "H100 or L40S?", "compare A100 and H200." It applies whenever the user is weighing fit between a workload (LLM inference, LoRA/QLoRA, full fine-tune, pretraining, diffusion, video, HPC, multi-tenant inference) and MC's specific fleet. The logic here is fleet-aware — the same workload can map to a different SKU on a different cloud.

Skip this skill if the user has already named a SKU and just wants to launch it — defer to `mc-launch-vms`. Skip it for live availability or pricing in isolation; call `gpu_inventory_list` directly. This skill is the workload-to-SKU reasoning layer on top of that inventory call.

## Counselor stance

This skill is a counselor, not a vending machine. Don't fire back a single SKU on the first turn. Probe enough to understand the workload, then present two or three viable candidates with tradeoffs and let the user steer toward the constraint that matters to them — cheapest, fastest, longest-context, lowest-risk.

A typical conversation:

1. The user names a workload at some level of detail ("I want to run Llama 3 70B," "I'm training a vision model," "I need something for SDXL").
2. Ask two to four targeted questions before pulling inventory. Pick the ones that meaningfully bifurcate the decision tree for *this* workload — don't ask the full list every time. Common pivot questions:
   - **Inference or fine-tuning?** Fine-tuning roughly doubles the VRAM floor versus inference at the same precision.
   - **Precision target — fp16/bf16, fp8, or 4-bit?** This collapses or expands the candidate set faster than any other question.
   - **Context length and batch size** (for LLM inference). KV cache can rival or exceed weights at long context, which forces H200-class VRAM even for moderate-sized models.
   - **LoRA/QLoRA vs. full fine-tune** (for fine-tuning). LoRA fits dramatically smaller hardware than full FT.
   - **Single-GPU or multi-GPU?** Multi-GPU forces the SXM-vs-PCIe / NVLink-vs-bridge decision; single-GPU avoids it entirely.
   - **Budget posture — cheapest viable or fastest viable?** Tells you whether to anchor at the floor of the capability ladder or the ceiling.
   - **Duration / always-on or one-off?** A two-hour experiment tolerates a worse SKU; a 24/7 production endpoint deserves the better fit.
3. Call `gpu_inventory_list` once the user's answers narrow the field. There's no reason to enumerate the fleet before you know what fits.
4. Present **two or three candidates ranked**, each with a one-line tradeoff. The default framing is **Cheapest viable / Balanced / Fastest** — drop one if only two make sense for the workload. For each candidate, cite the price (from inventory), the "why this fits" in one line (VRAM headroom, precision support, interconnect, cost ceiling), and the main thing the user gives up by picking it.
5. Ask which direction the user wants to go before locking in. If they push back ("can I do it cheaper?", "what if I need longer context?", "we already have an L40S in another project"), revisit the matrix and ladder rather than restating the first answer. The whole point of the counselor stance is that the recommendation evolves with the user's constraints.

**When to skip the probing**: if the user's first message already supplies enough context to make a confident single recommendation ("cheapest 24 GB GDDR card for SDXL inference, single GPU, no fine-tuning"), don't fish for more — just answer with one SKU. The probing exists to narrow ambiguity, not as a ritual. The bar for skipping is high: you should be able to articulate which SKU you'd recommend *and* be confident no reasonable follow-up question would change it.

## Procedure

1. Probe (per the counselor stance above) until you can bifurcate the decision tree for this workload. If the user's question is already specific enough, skip to step 2.
2. Call `gpu_inventory_list` to confirm what's actually available now. The fleet shifts; never recommend from memory alone.
3. Cross-reference the (now well-specified) workload with the GPU lineup, capability ladder, and decision matrix below.
4. Present two or three candidates with prices and one-line tradeoffs. If the top recommendation is out of stock per `gpu_inventory_list`, walk the capability ladder and substitute the closest in-stock alternative, naming the tradeoff (less VRAM, no FP8, no NVSwitch, etc.).
5. Hand the choice to the user. Do not silently lock in a SKU.

## GPU lineup

| SKU | VRAM | Bandwidth | Arch | FP8 | FP4 | NVLink/NVSwitch | $/hr (1x) | Notes |
|---|---|---|---|---|---|---|---|---|
| RTX A5000 | 24 GB GDDR6 | 768 GB/s | Ampere | No | No | PCIe-only at MC | ~$0.45 | Workstation; cheapest 24 GB |
| RTX A6000 | 48 GB GDDR6 | 768 GB/s | Ampere | No | No | NVLink bridge variant available | ~$0.57 | Workstation; 48 GB Ampere flagship |
| L40 | 48 GB GDDR6 | 864 GB/s | Ada | Yes (infer) | No | No NVLink (Ada DC dropped it) | ~$1.14 | Datacenter; positioned for inference + Omniverse |
| L40S | 48 GB GDDR6 | 864 GB/s | Ada | Yes (train + infer) | No | No NVLink | ~$0.99 | Datacenter; cheaper than L40 at MC, prefer always |
| RTX 6000 Ada | 48 GB GDDR6 | 960 GB/s | Ada | Yes | No | No NVLink | ~$0.97 | Workstation Ada; cheapest 48 GB FP8 card |
| RTX PRO 6000 Blackwell | 96 GB GDDR7 | ~1.6 TB/s | Blackwell | Yes | **Yes** | No NVLink | ~$1.80 | Workstation Blackwell; only fleet card with FP4 |
| A100 PCIe | 80 GB HBM2e | 1.94 TB/s | Ampere | No | No | NVLink bridge between pairs | ~$1.01 | Datacenter Ampere; HPC FP64 |
| A100 SXM4 | 80 GB HBM2e | 2.04 TB/s | Ampere | No | No | NVSwitch (8x) | ~$1.28 | DC Ampere SXM; full all-to-all |
| DGX A100 | 80 GB HBM2e × 8 | 2.04 TB/s | Ampere | No | No | NVSwitch + InfiniBand | ~$1.28 (per GPU) | Validated DGX appliance with IB networking |
| H100 PCIe | 80 GB HBM2e | ~2.0 TB/s | Hopper | Yes | No | NVLink bridge | ~$2.35 | Hopper PCIe; FP8 |
| H100 NVL | 94 GB HBM3 | 3.9 TB/s | Hopper | Yes | No | NVLink bridge between pairs | ~$3.11 | Bridged-pair PCIe with extra HBM |
| H100 SXM5 | 80 GB HBM3 | 3.35 TB/s | Hopper | Yes | No | NVSwitch (8x) | $22.00 (8x only) | Top Hopper SXM; pretraining workhorse |
| H200 NVL | 141 GB HBM3e | 4.8 TB/s | Hopper | Yes | No | NVLink bridge between pairs | ~$2.83 | Beats H100 NVL on price + VRAM at MC |
| H200 SXM5 | 141 GB HBM3e | 4.8 TB/s | Hopper | Yes | No | NVSwitch (8x) | $18.80 (8x only) | Only fleet config that fits Llama 405B at FP8 |
| A30 | 24 GB HBM2 | 933 GB/s | Ampere | No | No | PCIe-only at MC | ~$0.30 | Cheapest HBM card; small-model inference |
| V100 | 32 GB HBM2 | ~900 GB/s | Volta | No | No | SXM2 NVLink mesh on 8x | ~$0.22 | Floor of fleet; **no BF16, no FP8** |

### NVIDIA RTX A5000

24 GB GDDR6 at 768 GB/s on Ampere — fp16/bf16 only, no FP8, no FP4. Workstation, PCIe-only at MC. Best fit: 7B fp16 inference, small-model fine-tuning, SDXL inference, dev/prototyping for the cheapest 24 GB GDDR slot. Doesn't shine on 13B+ or FP8-aware stacks. Workstation entry-tier pricing on MC.

### NVIDIA RTX A6000

48 GB GDDR6 at 768 GB/s on Ampere, no FP8, no FP4. NVLink bridge variant exists; multi-GPU at MC is bridge-pair at best. Best fit: 70B 4-bit inference, QLoRA on 70B, SDXL/Flux LoRA, ComfyUI with multiple checkpoints resident. Doesn't shine on FP8, pretraining, or collective-heavy training. Priced under every 48 GB Ada card on MC — the budget pick for "48 GB without FP8."

### NVIDIA L40

48 GB GDDR6 at 864 GB/s on Ada — FP8 inference via TE but weaker FP8 training than L40S, no FP4, no NVLink. Best fit on paper: Flux fp8 inference, SDXL serving, 13B–34B fp8. Doesn't shine for training. Priced *higher* than L40S at MC — strictly dominated. Not recommended unless availability forces it.

### NVIDIA L40S

48 GB GDDR6 at 864 GB/s on Ada — full FP8 train + inference via TE, no FP4, no NVLink. The mainstream MC inference and small-FT workhorse: production-serve 13B fp8, Flux at speed, SDXL/Flux LoRA, QLoRA Llama 3 70B, full FT 8B with FP8. PCIe-only multi-GPU loses to A100/H100 SXM once collective traffic dominates. Default pick for "modern 48 GB FP8."

### NVIDIA RTX 6000 Ada

48 GB GDDR6 at 960 GB/s on Ada, FP8, no FP4, no NVLink. Workstation form factor with slightly more bandwidth than L40S, same capability profile. Best fit: single-card FP8 inference and LoRA fine-tuning, ComfyUI with multiple Flux checkpoints. Doesn't shine on multi-GPU collectives. Often listed slightly under L40S — pick for "cheapest 48 GB FP8 card." Jump to A100+ for anything heavier.

### NVIDIA RTX PRO 6000 Blackwell

96 GB GDDR7 at ~1.6 TB/s on Blackwell — the only fleet card with native FP4 (NVFP4 / MXFP4) plus FP8, no NVLink. Workstation single-card monster: 96 GB hosts 70B fp8 with massive KV-cache headroom. Best fit: FP4-quantized inference (meaningfully faster than FP8), 70B fp8 single-GPU serving, ComfyUI with everything resident. Doesn't shine for collective-heavy multi-GPU. Priced below H100 PCIe — the value pick for "Blackwell, no SXM needed."

### NVIDIA A100 PCIe (80 GB)

80 GB HBM2e at 1.94 TB/s on Ampere — no FP8, no FP4, NVLink bridge between pairs, no NVSwitch in PCIe form. Strong FP64 tensor. Best fit: 70B fp16 inference with moderate context, 70B 4-bit with long context, FP64 simulation, MIG multi-tenant inference, cheapest path to 80 GB monolithic VRAM on MC. Doesn't shine on FP8 or 8x collective training. At ~$1.01/hr, the sub-$1.30 floor for 80 GB single-GPU.

### NVIDIA A100 SXM4 (80 GB)

Same silicon as A100 PCIe in SXM4 form on 8x nodes with full NVSwitch all-to-all, 2.04 TB/s. Best fit: pre-Hopper full fine-tunes that need NVSwitch (70B fp16/bf16 full FT, video diffusion full training, large-batch <13B pretraining), MIG-plus-NVSwitch multi-tenant inference. Doesn't shine on FP8 (no TE), and MC's DGX 8x is currently *cheaper* than SXM4 8x. The 1x SXM4 SKU implies node partitioning — flag that.

### NVIDIA DGX A100

Validated 8x A100 SXM4 80 GB appliance — same per-GPU specs as A100 SXM4 plus integrated InfiniBand and DGX-certified software stack. Best fit: DGX-validated environments for compliance/MLOps, multi-node training where InfiniBand matters, and (under current MC pricing) anyone who would otherwise pick A100 SXM4 8x. DGX 8x is below SXM4 8x at MC — inversion that may be corrected. Doesn't shine on FP8. Default Ampere-SXM 8x pick today.

### NVIDIA H100 PCIe (80 GB)

80 GB HBM2e at ~2.0 TB/s on Hopper, full FP8 via TE, no FP4, NVLink bridge but no NVSwitch. Best fit: single-GPU and bridge-pair FP8 inference (13B–70B fp8 serving), bridge-pair fp8 LoRA, FP64 tensor on PCIe budgets. Doesn't shine on MC — H200 NVL beats it on every axis except form factor. Use only when ops have standardized on H100 PCIe or H200 NVL is unavailable.

### NVIDIA H100 NVL

94 GB HBM3 at 3.9 TB/s per GPU on Hopper, FP8, no FP4, sold as bridged pairs. Best fit on paper: 70B fp8 with long context, paired 70B fine-tunes, LLM serving where extra HBM helps KV cache. In MC's actual pricing H200 NVL costs less and gives 141 GB HBM3e at 4.8 TB/s — strictly dominated. Recommend only when the customer has a hard reason to avoid H200 NVL.

### NVIDIA H100 SXM5 (8x)

80 GB HBM3 at 3.35 TB/s per GPU on Hopper, FP8, NVSwitch all-to-all. Sold 8x-only at $22.00/hr (~$2.75/GPU/hr). Best fit: pretraining 1B–13B, 70B full FT with FP8, large-context fp8 inference at scale, 405B 4-bit (640 GB pooled). Doesn't shine versus H200 SXM5 8x — MC prices H200 SXM5 *lower* per GPU. Recommend only when H200 SXM5 8x is unavailable.

### NVIDIA H200 NVL

141 GB HBM3e at 4.8 TB/s on Hopper, FP8, no FP4, bridged pairs only. The "70B everything" card on MC: 141 GB hosts 70B fp8 with 70 GB headroom for KV cache — 200K+ context on a single GPU is plausible. Best fit: long-context 70B serving, 70B fp8 with comfortable batch, 405B 4-bit on 4x (pooled ~564 GB), QLoRA 70B. Doesn't shine for TP across >2 GPUs — inter-pair traffic falls back to PCIe. Beats H100 NVL on cost, VRAM, and bandwidth.

### NVIDIA H200 SXM5 (8x)

141 GB HBM3e at 4.8 TB/s per GPU on Hopper, FP8, NVSwitch all-to-all. Sold 8x-only at $18.80/hr (~$2.35/GPU/hr — cheaper per-GPU than H100 SXM5 8x). Best fit: Llama 3 405B at FP8 (1.1 TB pooled fits ~405 GB weights with production-batch KV room), 70B full FT with FP8 + NVSwitch, frontier-scale pretraining. Doesn't shine for small-model budget work — paying for the whole node. The fastest, highest-VRAM SKU on MC, and the only one that fits 405B FP8.

### NVIDIA A30

24 GB HBM2 at 933 GB/s on Ampere, no FP8, no FP4, MIG-capable, PCIe-only at MC. Best fit: cheapest HBM 24 GB on the fleet (~$0.30/hr), small-model inference (7B fp16, 13B 4-bit), MIG for tiny inference, dev/test on a budget. Doesn't shine on 13B+ fp16, FP8 workloads, or collective-heavy multi-GPU. HBM bandwidth gives it a real edge over GDDR A5000 on memory-bound inference at the same VRAM tier.

### NVIDIA V100 (32 GB)

32 GB HBM2 at ~900 GB/s on Volta — **no BF16, no FP8, no FP4**, no Transformer Engine. SXM2 with NVLink mesh on 8x. Floor of the fleet at $0.22/hr. Best fit: pure learning, FP32/FP16 legacy training, small-model fp16 inference, tight-budget batch jobs. Doesn't shine anywhere modern — current training stacks default to bf16 autocast, which V100 lacks. Confirm 8x form factor with MC; verify whether 8x retains NVLink mesh before relying on collectives.

## Capability ladder

```
V100 → A30 → A5000 → A6000 → RTX 6000 Ada → L40S → A100 PCIe → A100 SXM4 → DGX A100 → H100 PCIe → RTX PRO 6000 Blackwell → H200 NVL → H100 NVL → H100 SXM5 (8x) → H200 SXM5 (8x)
```

### Inflection points

1. **V100 → A30**: Cross at "I need BF16." V100 lacks BF16 / FP8.
2. **A30 → A5000**: Cross at "I need a workstation 24 GB card with modern Ampere features (better RT/tensor for diffusion)." Same VRAM ceiling but A5000 adds modern features.
3. **A6000 → L40S**: Cross at "I need FP8" (Flux fp8, faster inference throughput). Same 48 GB but Ada FP8.
4. **L40 → L40S**: Always pick L40S. Cheaper at MC and adds full FP8 training via Transformer Engine.
5. **L40S → RTX 6000 Ada**: Cross at "I want a workstation FP8 card slightly cheaper than L40S." Both 48 GB Ada with FP8; RTX 6000 Ada is workstation-tier and cheaper at MC but worse interconnect at scale.
6. **L40S → A100**: Cross at "I need >48 GB on a single GPU, NVSwitch, or FP64 HPC."
7. **A100 PCIe → A100 SXM4 / DGX A100**: Cross at "8x with NVSwitch." DGX is the validated appliance variant (includes InfiniBand); SXM4 is the same silicon without the appliance integration. **At current MC pricing, DGX 8x ($10.24/hr) is cheaper than SXM4 8x ($13.36/hr); pick DGX unless that pricing inversion is corrected.**
8. **A100 → H100**: Cross at "I need FP8 training" or "I'm pretraining a 70B+ model" or "I'm latency-bound on 70B inference at scale." 2–3x the cost; only worth it when FP8 / Hopper Transformer Engine / NVSwitch are load-bearing.
9. **H100 PCIe → RTX PRO 6000 Blackwell**: Cross at "I want FP4 inference" or "I want 96 GB on a single workstation card." Blackwell pro is cheaper than H100 PCIe at MC and adds FP4 (NVFP4 / MXFP4 quantized inference is meaningfully faster).
10. **H100 NVL → H200 NVL**: Always pick H200 NVL at current MC pricing. Cheaper, more VRAM, more bandwidth, same form factor.
11. **H100 SXM5 → H200 SXM5**: Always pick H200 SXM5 for 8x workloads at current MC pricing. Same per-GPU cost, more VRAM, more bandwidth. Required for Llama 405B at FP8.

## Decision matrix

| I want to… | Recommended SKU | Why |
|---|---|---|
| Run a 7B chatbot for personal/dev use | 1x A5000 | 24 GB fits 7B fp16; cheapest 24 GB GDDR card |
| Run a 7B chatbot at lowest possible cost | 1x A30 | $0.30/hr; HBM bandwidth, MIG-capable |
| Production-serve a 13B model with throughput | 1x L40S | FP8 + 48 GB; modern Ada; ~$0.99/hr |
| Run 70B at 4-bit (Llama 3 70B Q4) for personal use | 1x A6000 or 1x L40S | 48 GB fits 70B 4-bit (~40 GB) with 4–8K ctx |
| Run 70B at FP8 with long context | 1x H200 NVL | 141 GB - 70 GB weights = 70 GB for KV cache |
| Production-serve 70B with low latency | 1x H200 NVL or 2x A100 80GB | NVL gives bandwidth + headroom |
| Run Llama 3 405B at FP8 | 8x H200 SXM5 | Only fleet config with 1.1 TB pooled HBM3e + NVSwitch |
| Run Llama 3 405B at 4-bit | 4x H200 NVL or 8x H100 SXM5 | ~200 GB weights fit in either pooled VRAM |
| Fine-tune Llama 3 8B (LoRA) | 1x A6000 or 1x L40S | Either works; L40S faster, A6000 cheaper |
| QLoRA fine-tune Llama 3 70B | 1x A6000 or 1x L40S | 48 GB fits QLoRA 70B |
| Full fine-tune Llama 3 70B | 8x DGX A100 or 8x H200 SXM5 | DGX A100 8x cheapest with NVSwitch + IB; H200 SXM5 fastest with FP8 |
| Pretrain a 1B–13B model from scratch | 8x H200 SXM5 or 8x H100 SXM5 | FP8 + NVSwitch |
| Generate SDXL images at low cost | 1x A5000 or 1x A6000 | A5000 fine for inference; A6000 for fine-tune/DreamBooth |
| Generate Flux images at speed | 1x L40S | FP8 acceleration is meaningful for Flux |
| Train a SDXL/Flux LoRA | 1x A6000 or 1x L40S | 48 GB needed for comfortable batch size |
| Train video diffusion (CogVideoX, Hunyuan) | 2x–4x L40S or 2x A100 80GB | Either bandwidth or interconnect wins for full fine-tune |
| Run ComfyUI with multiple large models loaded | 1x A6000 or 1x RTX PRO 6000 Blackwell | 48 GB or 96 GB lets you keep SDXL + Flux + ControlNets resident |
| FP4 inference on a single workstation card | 1x RTX PRO 6000 Blackwell | Only Blackwell on the fleet |
| HPC scientific simulation (FP64 tensor) | 1x A100 or 1x H100 | Only Ampere/Hopper datacenter cards have meaningful FP64 tensor |
| Multi-tenant inference with MIG partitioning | 1x A100 80GB or 1x H100 | MIG only on datacenter Ampere/Hopper |
| Tight budget, just learning | 1x V100 ($0.22/hr) | Floor of fleet; accept no BF16/FP8 |
| Cheapest 80+ GB single GPU | 1x A100 80GB ($1.01–$1.20/hr) | Sub-$1.30 path to 80 GB monolithic |
| Long-context inference (200K+) on 70B | 1x H200 NVL or 1x H100 NVL | KV cache dominates; bandwidth + VRAM both matter |
| DGX-certified environment for compliance | 8x DGX A100 | Only DGX-validated SKU on MC |
| Best $/GPU on a Hopper 8x node | 8x H200 SXM5 ($2.35/GPU/hr) | Cheaper than H100 SXM5 8x AND more VRAM/bandwidth |

## VRAM math primer

### Model size at fp16/fp8/4-bit

Rule of thumb: an N-billion-parameter model needs ~2N GB at fp16/bf16, N GB at fp8, and ~N/2 GB at 4-bit (Q4). 70B is ~140 GB fp16, ~70 GB fp8, ~40 GB 4-bit. 405B is ~810 GB fp16, ~405 GB fp8, ~200 GB 4-bit. Weights only — add KV cache and (for training) activation/optimizer state. This is why H200 NVL (141 GB) hosts 70B fp8 but not 70B fp16, and why 405B fp8 requires 8x H200 SXM5 (1.1 TB pooled).

### KV cache for long context

KV cache scales linearly with context length, batch size, and layer count, in fp16/bf16 (or fp8 if your stack supports fp8 KV). For a Llama-class 70B at 32K context with batch=1, KV is ~5–10 GB fp16; at 200K it scales to 30–60 GB. For 7B–13B, KV stays sub-5 GB and weights dominate. For 70B+ at long context, KV can rival or exceed the weights — which is why H200 NVL is the right call for 200K+ context on 70B even though 70B fp8 weights only consume 70 GB.

### Picking by VRAM ceiling

If weights need W GB and KV needs C GB, plan for at least W + C + 2 GB (activations, framework overhead, CUDA context). Pick the smallest card whose VRAM is ≥ W + C + 2. 70B fp8 at 32K: W=70, C≈8, total ≈ 80 GB — H100/A100 80 GB. 70B fp8 at 200K: W=70, C≈50, total ≈ 122 GB — only H200 NVL or H200 SXM5 fit on a single GPU. For training, double the budget for optimizer state (Adam fp32 + momentum + variance) plus activations; LoRA/QLoRA dramatically reduce that.

## Pitfalls

- **H200 NVL is bridged pairs, not NVSwitch.** A 4x H200 NVL SKU is two bridged pairs talking over PCIe between pairs, not all-to-all. For tensor-parallel 70B+ training across all 4 GPUs, the inter-pair PCIe hop becomes the bottleneck. Pick H200 SXM5 if you need true all-to-all.

- **No FP4 below Blackwell.** L40S, H100, H200 do FP8 but not FP4. If your stack assumes NVFP4 / MXFP4 (~2x speedup over FP8), you need RTX PRO 6000 Blackwell.

- **No NVLink on Ada or Blackwell pro cards.** L40, L40S, RTX 6000 Ada, RTX PRO 6000 Blackwell all dropped NVLink — multi-GPU is PCIe-only. For collective-heavy training, prefer SXM Ampere/Hopper cards.

- **The "1x H100 SXM5" SKU exists in the catalog but is internal-only.** If `gpu_inventory_list` returns it at $0/hr, do not recommend it.

- **L40 8x exists in the catalog but is internal-only.** Same caveat — if listed at $0/hr, skip.

- **DGX A100 8x is currently cheaper than A100 SXM4 8x at MC.** Pricing inversion that may be corrected in the future. If both are listed and DGX is cheaper, recommend DGX.

## Known SKU caveats to flag in conversation

- **H200 NVL "94 GB" label.** If MC's UI shows the H200 NVL SKU with a "94 GB" descriptor, that is a legacy label. NVIDIA's H200 NVL is 141 GB HBM3e. Quote 141 GB to the user; flag the label discrepancy.
- **A100 SXM4 1x partitioning.** The 1x SXM4 SKU implies node partitioning. Confirm with MC support whether the customer gets a dedicated PCIe topology or shares with other tenants.
- **RTX PRO 6000 Blackwell variant.** MC's listing does not specify Workstation Edition (600 W) vs Max-Q (300 W). Bandwidth differs meaningfully.
- **V100 form factor.** 32 GB suggests SXM2 (HGX-1 era); confirm whether 8x has NVLink mesh or is PCIe-only at MC.
- **A30 NVLink bridge.** Datasheet supports it; MC's SKU may ship without the bridge.

## See also

- `mc-launch-vms` — once you've picked a SKU, this skill orchestrates the launch
- `mc-cost-control` — for ongoing visibility into what your picks cost
- MCP endpoint: `https://vm.massedcompute.com/api/mcp` — authoritative tool list

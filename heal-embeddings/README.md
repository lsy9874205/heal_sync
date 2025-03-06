---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:247936
- loss:CosineSimilarityLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: "**Intervention costs**, including:\n   - Medication costs\n  \
    \ - Provider time\n   - Peer navigator time and expenses\n   - Program administration"
  sentences:
  - '4.2 Inclusion Criteria


    Patients must meet all of the following inclusion criteria to be eligible for
    the study:'
  - "**MOUD Type**:\n   - Methadone\n   - Buprenorphine\n   - Naltrexone"
  - Pregnancy (pregnant patients will be referred to specialized obstetric addiction
    services)
- source_sentence: 4.2 Exclusion Criteria
  sentences:
  - 8.3 Follow-Up Visits
  - To assess retention in addiction treatment between study arms at 90 and 180 days
    post-randomization.
  - ETHICAL CONSIDERATIONS
- source_sentence: 8.3 Specific Safety Concerns and Monitoring
  sentences:
  - '11.1.2 Steering Committee


    Composition:

    - Executive Committee members

    - Site investigators

    - Patient/community representatives

    - Key co-investigators


    Responsibilities:

    - Protocol revisions

    - Implementation monitoring

    - Recruitment oversight

    - Review of study progress

    - Addressing operational challenges'
  - Chronic non-cancer pain (defined as pain lasting ≥3 months)
  - 'Cancer-related pain (exception: patients with a history of cancer who are in
    remission for ≥5 years and whose pain is unrelated to cancer)'
- source_sentence: '7.1 Randomization


    Participants will be randomly assigned in a 1:1 ratio to receive either BUP-NX
    or XR-NTX using a computer-generated randomization sequence with permuted blocks
    of varying sizes. Randomization will be stratified by site and by opioid type
    (short-acting prescription opioids, heroin, or fentanyl as primary opioid of use).'
  sentences:
  - '**Privacy and Confidentiality**: There is a risk of breach of confidentiality
    or privacy related to the collection of sensitive information about substance
    use and mental health.'
  - '3.2 Study Sites


    The study will be conducted at six Emergency Departments:'
  - '3.4 Recruitment Strategy


    Potential participants will be identified through:

    - Referrals from emergency departments, hospital discharge planning, detoxification
    centers, and other healthcare providers

    - Self-referral through community outreach and advertisements

    - Screening of electronic health records to identify patients with OUD'
- source_sentence: To evaluate the cost-effectiveness of ED-initiated buprenorphine
    with peer navigator support compared to enhanced referral to treatment.
  sentences:
  - '12.1 Data Collection


    Data will be collected using electronic case report forms (eCRFs) in a secure,
    web-based data management system. The system will include range checks, consistency
    checks, and validation rules to ensure data quality.'
  - Concerns about withdrawal precipitation
  - '11.1.2 Steering Committee


    Composition:

    - Executive Committee members

    - Site investigators

    - Patient/community representatives

    - Key co-investigators


    Responsibilities:

    - Protocol revisions

    - Implementation monitoring

    - Recruitment oversight

    - Review of study progress

    - Addressing operational challenges'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision fa97f6e7cb1a59073dff9e6b13e2715cf7475ac9 -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/UKPLab/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 256, 'do_lower_case': False}) with Transformer model: BertModel 
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
  (2): Normalize()
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'To evaluate the cost-effectiveness of ED-initiated buprenorphine with peer navigator support compared to enhanced referral to treatment.',
    'Concerns about withdrawal precipitation',
    '11.1.2 Steering Committee\n\nComposition:\n- Executive Committee members\n- Site investigators\n- Patient/community representatives\n- Key co-investigators\n\nResponsibilities:\n- Protocol revisions\n- Implementation monitoring\n- Recruitment oversight\n- Review of study progress\n- Addressing operational challenges',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities.shape)
# [3, 3]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 247,936 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                         | sentence_1                                                                         | label                                                         |
  |:--------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:--------------------------------------------------------------|
  | type    | string                                                                             | string                                                                             | float                                                         |
  | details | <ul><li>min: 3 tokens</li><li>mean: 48.16 tokens</li><li>max: 256 tokens</li></ul> | <ul><li>min: 3 tokens</li><li>mean: 44.76 tokens</li><li>max: 256 tokens</li></ul> | <ul><li>min: 0.5</li><li>mean: 0.5</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                             | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                      | label            |
  |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>10.4 Participant Confidentiality</code>                                                                                                                                                                                                                                                                                                                          | <code>9.1.1 Data and Safety Monitoring Board (DSMB)<br><br>An independent DSMB will be established, consisting of experts in emergency medicine, addiction medicine, biostatistics, and ethics. The DSMB will:<br>- Review and approve the monitoring plan<br>- Meet at least annually to review study progress and safety<br>- Review any serious adverse events<br>- Make recommendations regarding study continuation or modification</code> | <code>0.5</code> |
  | <code>7.1 Randomization<br><br>Participants will be randomly assigned in a 1:1 ratio to receive either BUP-NX or XR-NTX using a computer-generated randomization sequence with permuted blocks of varying sizes. Randomization will be stratified by site and by opioid type (short-acting prescription opioids, heroin, or fentanyl as primary opioid of use).</code> | <code>10.3 Risk Mitigation</code>                                                                                                                                                                                                                                                                                                                                                                                                               | <code>0.5</code> |
  | <code>11.1 Study Leadership and Governance</code>                                                                                                                                                                                                                                                                                                                      | <code>To examine patient perspectives on intervention acceptability and barriers/facilitators to engagement through qualitative interviews with a subset of participants.</code>                                                                                                                                                                                                                                                                | <code>0.5</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 3
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `dispatch_batches`: None
- `split_batches`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin

</details>

### Training Logs
| Epoch  | Step  | Training Loss |
|:------:|:-----:|:-------------:|
| 0.0323 | 500   | 0.0107        |
| 0.0645 | 1000  | 0.0025        |
| 0.0968 | 1500  | 0.0023        |
| 0.1291 | 2000  | 0.0023        |
| 0.1613 | 2500  | 0.0021        |
| 0.1936 | 3000  | 0.002         |
| 0.2259 | 3500  | 0.0018        |
| 0.2581 | 4000  | 0.0018        |
| 0.2904 | 4500  | 0.0017        |
| 0.3227 | 5000  | 0.0017        |
| 0.3549 | 5500  | 0.0017        |
| 0.3872 | 6000  | 0.0016        |
| 0.4195 | 6500  | 0.0015        |
| 0.4517 | 7000  | 0.0016        |
| 0.4840 | 7500  | 0.0016        |
| 0.5163 | 8000  | 0.0015        |
| 0.5485 | 8500  | 0.0015        |
| 0.5808 | 9000  | 0.0014        |
| 0.6131 | 9500  | 0.0015        |
| 0.6453 | 10000 | 0.0015        |
| 0.6776 | 10500 | 0.0014        |
| 0.7099 | 11000 | 0.0015        |
| 0.7421 | 11500 | 0.0013        |
| 0.7744 | 12000 | 0.0013        |
| 0.8067 | 12500 | 0.0013        |
| 0.8389 | 13000 | 0.0013        |
| 0.8712 | 13500 | 0.0013        |
| 0.9035 | 14000 | 0.0013        |
| 0.9357 | 14500 | 0.0013        |
| 0.9680 | 15000 | 0.0012        |
| 1.0003 | 15500 | 0.0012        |
| 1.0325 | 16000 | 0.0011        |
| 1.0648 | 16500 | 0.0011        |
| 1.0971 | 17000 | 0.0011        |
| 1.1293 | 17500 | 0.0011        |
| 1.1616 | 18000 | 0.0011        |
| 1.1939 | 18500 | 0.001         |
| 1.2261 | 19000 | 0.001         |
| 1.2584 | 19500 | 0.0011        |
| 1.2907 | 20000 | 0.001         |
| 1.3229 | 20500 | 0.0011        |
| 1.3552 | 21000 | 0.001         |
| 1.3875 | 21500 | 0.001         |
| 1.4197 | 22000 | 0.001         |
| 1.4520 | 22500 | 0.001         |
| 1.4843 | 23000 | 0.001         |
| 1.5165 | 23500 | 0.0009        |
| 1.5488 | 24000 | 0.001         |
| 1.5811 | 24500 | 0.001         |
| 1.6133 | 25000 | 0.0009        |
| 1.6456 | 25500 | 0.001         |
| 1.6779 | 26000 | 0.001         |
| 1.7101 | 26500 | 0.001         |
| 1.7424 | 27000 | 0.001         |
| 1.7747 | 27500 | 0.001         |
| 1.8069 | 28000 | 0.001         |
| 1.8392 | 28500 | 0.001         |
| 1.8715 | 29000 | 0.001         |
| 1.9037 | 29500 | 0.0009        |
| 1.9360 | 30000 | 0.0009        |
| 1.9682 | 30500 | 0.0009        |
| 2.0005 | 31000 | 0.0009        |
| 2.0328 | 31500 | 0.0008        |
| 2.0650 | 32000 | 0.0008        |
| 2.0973 | 32500 | 0.0007        |
| 2.1296 | 33000 | 0.0008        |
| 2.1618 | 33500 | 0.0008        |
| 2.1941 | 34000 | 0.0008        |
| 2.2264 | 34500 | 0.0008        |
| 2.2586 | 35000 | 0.0008        |
| 2.2909 | 35500 | 0.0008        |
| 2.3232 | 36000 | 0.0008        |
| 2.3554 | 36500 | 0.0008        |
| 2.3877 | 37000 | 0.0008        |
| 2.4200 | 37500 | 0.0008        |
| 2.4522 | 38000 | 0.0008        |
| 2.4845 | 38500 | 0.0008        |
| 2.5168 | 39000 | 0.0008        |
| 2.5490 | 39500 | 0.0008        |
| 2.5813 | 40000 | 0.0007        |
| 2.6136 | 40500 | 0.0008        |
| 2.6458 | 41000 | 0.0008        |
| 2.6781 | 41500 | 0.0007        |
| 2.7104 | 42000 | 0.0007        |
| 2.7426 | 42500 | 0.0007        |
| 2.7749 | 43000 | 0.0008        |
| 2.8072 | 43500 | 0.0008        |
| 2.8394 | 44000 | 0.0007        |
| 2.8717 | 44500 | 0.0008        |
| 2.9040 | 45000 | 0.0008        |
| 2.9362 | 45500 | 0.0007        |
| 2.9685 | 46000 | 0.0007        |


### Framework Versions
- Python: 3.13.2
- Sentence Transformers: 3.4.1
- Transformers: 4.49.0
- PyTorch: 2.6.0
- Accelerate: 1.4.0
- Datasets: 3.3.2
- Tokenizers: 0.21.0

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->

# HEAL Protocol Embeddings

This model is fine-tuned from all-MiniLM-L6-v2 on HEAL Initiative clinical protocols.

## Performance Evaluation

Comparison with OpenAI embeddings:

| Metric | OpenAI | Fine-tuned | Change |
|--------|--------|------------|---------|
| Faithfulness | 0.667 | 0.833 | ⬆️ +0.166 |
| Answer Relevancy | 0.986 | 0.986 | = |
| Context Precision | 1.000 | 1.000 | = |
| Context Recall | 1.000 | 0.000 | ⬇️ -1.000 |

### Key Findings
- Improved faithfulness to source material
- Maintained high answer relevancy
- Trade-off in context recall

## Future Improvements

1. Retrieval Strategy
   - Implement hybrid search combining semantic and keyword matching
   - Add re-ranking for better result ordering

2. Model Architecture
   - Experiment with larger base models
   - Fine-tune with domain-specific loss functions

3. Data Processing
   - Optimize chunking strategy
   - Increase training data diversity
python -m src.pipeline.dataset_preperation.Prepare_training_data.main

llamafactory-cli train examples/train_lora/REWRITE_QUERY_MODEL_lora_sft.yaml
llamafactory-cli train examples/train_lora/SELECTOR_MODEL_lora_sft.yaml
llamafactory-cli train examples/train_lora/GENERATION_MODEL_lora_sft.yaml

llamafactory-cli export examples/merge_lora/generator_lora_sft.yaml
llamafactory-cli export examples/merge_lora/selector_lora_sft.yaml
llamafactory-cli export examples/merge_lora/rewriter_lora_sft.yaml


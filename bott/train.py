from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import os
from huggingface_hub import login
login("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")


model_name = "distilgpt2"


tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token 

model = AutoModelForCausalLM.from_pretrained(model_name)

print("Model and tokenizer loaded")

if not os.path.exists("data.txt"):
    raise FileNotFoundError("data.txt not found!")

dataset = load_dataset('text', data_files={'train': 'data.txt'})
print(f"Loaded dataset: {len(dataset['train'])} examples")

for i in range(min(3, len(dataset['train']))):
    print(f"\n🔹 Sample {i+1}:")
    print(dataset['train'][i]['text'])

def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

print("Tokenization completed")


data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./model",
    num_train_epochs=5,
    per_device_train_batch_size=2,
    save_total_limit=1,
    logging_dir='./logs',
    logging_steps=10,
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    data_collator=data_collator,
)

print("Starting training...")
trainer.train()
print("Training complete")

trainer.save_model("./model")
tokenizer.save_pretrained("./model")

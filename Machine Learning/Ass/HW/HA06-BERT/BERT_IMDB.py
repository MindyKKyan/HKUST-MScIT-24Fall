# HKUST 24fall
# CSIT5910 Machine Learning
# Hands-on Assignment 6: BERT
# Mingzhen JIANG 
# 21108128

import pandas as pd
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import BertTokenizerFast, BertForSequenceClassification, Trainer, TrainingArguments

# Specify GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load IMDB Dataset
df = pd.read_csv('IMDB Dataset.csv')
df['label'] = df['sentiment'].map({'positive': 1, 'negative': 0})

# Shuffle and split the dataset
train_text, temp_text, train_labels, temp_labels = train_test_split(df['review'], df['label'],
                                                                    random_state=42, test_size=0.3, stratify=df['label'])
val_text, test_text, val_labels, test_labels = train_test_split(temp_text, temp_labels,
                                                                random_state=42, test_size=0.5, stratify=temp_labels)

# Load the BERT tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

# Tokenize the inputs
max_length = 80

train_encodings = tokenizer(train_text.tolist(), truncation=True, padding=True, max_length=max_length)
val_encodings = tokenizer(val_text.tolist(), truncation=True, padding=True, max_length=max_length)
test_encodings = tokenizer(test_text.tolist(), truncation=True, padding=True, max_length=max_length)

# Create a dataset class
class IMDBDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = IMDBDataset(train_encodings, train_labels.tolist())
val_dataset = IMDBDataset(val_encodings, val_labels.tolist())
test_dataset = IMDBDataset(test_encodings, test_labels.tolist())

# Set up the model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch",
)

# Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# Fine-tuning
trainer.train()

# Evaluate the model
trainer.evaluate()

# Predict on the test set
predictions, true_labels, _ = trainer.predict(test_dataset)

# Convert predictions to binary labels
pred_labels = np.argmax(predictions, axis=1)

# Print classification report
print(classification_report(true_labels, pred_labels))

# Save the model
model.save_pretrained('./sentiment_model')
tokenizer.save_pretrained('./sentiment_model')

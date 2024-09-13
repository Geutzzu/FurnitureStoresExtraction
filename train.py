# this notebook was used as a reference for this script: https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/token_classification.ipynb#scrollTo=zVvslsfMIrIh
import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification
from datasets import Dataset
import evaluate
import numpy as np
from sklearn.model_selection import train_test_split


model_checkpoint = "distilbert-base-uncased"
batch_size = 16

label_all_tokens = False
label_map = {'O': 0, 'B-PROD': 1, 'I-PROD': 2} # bert expects labels to be in the form of integers
reverse_label_map = {v: k for k, v in label_map.items()} # we will use this to convert the model's output back to the original labels ffor metrics

def read_conll_file(file_path):
    sentences = []
    labels = []
    sentence = []
    label = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Skip blank lines (end of a sentence)
            if line.strip() == "":
                if sentence:  # Add the sentence and its labels to the list
                    sentences.append(sentence)
                    labels.append(label)
                    sentence = []
                    label = []
            else:
                # Safely split the line and check if it has the expected number of columns
                parts = line.split()

                if len(parts) == 4:  # We expect 4 columns: token, column 2, column 3, label
                    token, _, _, ner_label = parts
                    if ner_label == "B-I-PROD":
                        ner_label = "I-PROD"
                    if ner_label == "B-B-PROD":
                        ner_label = "B-PROD"
                    if ner_label == "I-B-PROD":
                        ner_label = "I-PROD"
                    if ner_label == "I-I-PROD":
                        ner_label = "I-PROD"

                elif len(parts) == 3:  # If there's a missing column, handle it
                    token, _, ner_label = parts
                    if ner_label == "B-I-PROD":
                        ner_label = "I-PROD"
                    if ner_label == "B-B-PROD":
                        ner_label = "B-PROD"
                    if ner_label == "I-B-PROD":
                        ner_label = "I-PROD"
                    if ner_label == "I-I-PROD":
                        ner_label = "I-PROD"
                else:
                    # Handle unexpected lines
                    print(f"Skipping line: {line.strip()}")
                    continue

                # Add the token and its label to the sentence
                sentence.append(token)
                label.append(ner_label)

        # If there's an unfinished sentence at the end of the file
        if sentence:
            sentences.append(sentence)
            labels.append(label)

    for i in range(len(labels)):
        for j in range(len(labels[i])):
            labels[i][j] = label_map[labels[i][j]]

    return sentences, labels


train_sentences, train_labels = read_conll_file("data/training_data_v1.conll")


# Load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
assert isinstance(tokenizer, transformers.PreTrainedTokenizerFast)

# this method aligns the labels after tokenization (some words may have been split into multiple tokens + the 2 special tokens)
def tokenize_and_align_labels(train_sentences, train_labels):
    tokenized_inputs = tokenizer(train_sentences, truncation=True, is_split_into_words=True)

    labels = []
    for i, label in enumerate(train_labels):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            # Special tokens have a word id that is None. We set the label to -100 so they are automatically
            # ignored in the loss function.
            if word_idx is None:
                label_ids.append(-100)
            # We set the label for the first token of each word.
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            # For the other tokens in a word, we set the label to either the current label or -100, depending on
            # the label_all_tokens flag.
            else:
                label_ids.append(label[word_idx] if label_all_tokens else -100)
            previous_word_idx = word_idx

        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs


# split the train_sentences and train_labels before tokenization
train_sentences_split, test_sentences_split, train_labels_split, test_labels_split = train_test_split(
    train_sentences, train_labels, test_size=0.2
)

# tokenize and align labels for both training and test datasets
train_data = tokenize_and_align_labels(train_sentences_split, train_labels_split)
test_data = tokenize_and_align_labels(test_sentences_split, test_labels_split)

# convert the tokenized data to Hugging Face Dataset format
train_dataset = Dataset.from_dict(train_data)
test_dataset = Dataset.from_dict(test_data)


# Now we load the model

model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, num_labels=len(label_map))

model_name = model_checkpoint.split("/")[-1]
args = TrainingArguments(
    f"{model_name}-for-product-extraction",
    evaluation_strategy = "epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=10,
    weight_decay=0.01,
)

data_collator = DataCollatorForTokenClassification(tokenizer)

metric = evaluate.load("seqeval")

def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    # Remove ignored index (special tokens)
    true_predictions = [
        [reverse_label_map[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [reverse_label_map[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }


trainer = Trainer(
    model,
    args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()


print(trainer.evaluate())
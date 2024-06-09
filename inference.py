from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import torch

# Load the model and tokenizer
model_name = "qwen2-vtb/checkpoint-500"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  

model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load the CSV file
df = pd.read_csv('test_set.csv')

# Assuming the CSV has a column named 'Content'
prompts = df['Content'].tolist()[:5]

# Function to generate a response with a length of 100 tokens
def generate_response(prompt, max_tokens=100):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}  # Move tensors to the appropriate device
    generation_config = {
        'max_length': max_tokens + inputs['input_ids'].shape[1],  # Adjust for input length
        'do_sample': False,
        # Uncomment and adjust these parameters as needed:
        # 'top_k': 50,
        # 'top_p': 0.95,
        # 'temperature': 0.7,
    }
    outputs = model.generate(**inputs, **generation_config)
    generated_tokens = outputs[:, inputs['input_ids'].shape[1]:]
    response = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
    return response

# Generate responses for all prompts in the CSV
responses = [generate_response(prompt) for prompt in prompts]

# Add the responses back to the dataframe
df['response'] = responses[:5]  # Ensure alignment with the number of prompts processed

# Save the dataframe with responses to a new CSV file
df.to_csv('output_with_responses.csv', index=False)

print("Responses generated and saved to 'output_with_responses.csv'")
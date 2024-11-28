from transformers import pipeline, AutoTokenizer,AutoModelForSeq2SeqLM
def load_model():
    #local model for text generation.
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return pipeline("text2text-generation",model=model,tokenizer=tokenizer,device=0)
if __name__ =="__main__":
    nlp = load_model()
    test_query = "write a python code to create a bar chart from a dataset with columns and region and revenue"
    response = nlp(test_query)
    print("generated code:",response[0]['generated_text'])
    print(response)
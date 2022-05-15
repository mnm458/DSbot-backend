import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import Flask, request, jsonify
from flask_restful import reqparse, Resource, Api
from flask_caching import Cache
import json
import secrets
import string
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600   # 1 hour == 3600 s
}


model_name = "microsoft/DialoGPT-large"
# model_name = "microsoft/DialoGPT-medium"
# model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

app = Flask(__name__)
api = Api(app)
app.config.from_mapping(config)
cache = Cache(app)

parser = reqparse.RequestParser()


class InputData(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        # take user input
        text = json_data["input"]
        token = json_data["token"]
        output = ''

        # get data from cache
        chat_history_ids_str = []
        # step = cache.get("step")
        # create new token
        if len(token) == 0:
            #no need to reset chat histroy
            token = ''.join(secrets.choice(
                string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
            chat_history_ids_str.append(text)
        else:
            #reset cache at 4
            cache.delete("chat_history_ids_str_"+token)
            chat_history_ids_str = []
            chat_history_ids_json_str = cache.get(
                "chat_history_ids_str_"+token)
            if chat_history_ids_json_str is None:
                chat_history_ids_str.append(text)
            else:
                chat_history_ids_str = json.loads(chat_history_ids_json_str)
                chat_history_ids_str.append(text)
        for step in range(0, len(chat_history_ids_str)):
            # encode the input and add end of string token
            input_ids = tokenizer.encode(
                chat_history_ids_str[step] + tokenizer.eos_token, return_tensors="pt")
            # concatenate new user input with chat history (if there is)
            bot_input_ids = torch.cat(
                [chat_history_ids, input_ids], dim=-1) if step > 0 else input_ids
            # generate a bot response
            chat_history_ids = model.generate(
                bot_input_ids,
                max_length=1000,
                do_sample=True,
                top_p=0.95,
                top_k=20,
                temperature=0.75,
                pad_token_id=tokenizer.eos_token_id
            )
            # print the output
            output = tokenizer.decode(
                chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

        # set data to cache
        cache.set("chat_history_ids_str_"+token,
                  json.dumps(chat_history_ids_str))
        return jsonify({"result": json.dumps(output), "token": token})


api.add_resource(InputData, '/api/v1/input')


class Echo(Resource):
    def get(self, text):
        return text


api.add_resource(Echo, '/echo/<text>')

# last 5 interactions with the chatbots
class Clear(Resource):
    def get(self, token):
        cache.delete("step_"+token)
        cache.delete("chat_history_ids_str_"+token) 
        return 'Cleared'


api.add_resource(Clear, '/clear/<token>')

#  Main
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)

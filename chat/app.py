from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient;
import urllib;
from Location import completeaddress;
import smtplib,ssl;
from email.mime.text import MIMEText;
from email.mime.multipart import MIMEMultipart;
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json


with open("intents.json") as file:
    data = json.load(file)



words = []
labels = []
docs_x = []
docs_y = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        wrds = nltk.word_tokenize(pattern)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent["tag"])

    if intent["tag"] not in labels:
        labels.append(intent["tag"])

words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

labels = sorted(labels)

training = []
output = []

out_empty = [0 for _ in range(len(labels))]

for x, doc in enumerate(docs_x):
    bag = []

    wrds = [stemmer.stem(w.lower()) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)

    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)


training = numpy.array(training)
output = numpy.array(output)


net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


# def chat():
#     print("Start talking with the bot (type quit to stop)!")
#     while True:
#         inp = input("You: ")
#         if inp.lower() == "quit":
#             break
#
#         results = model.predict([bag_of_words(inp, words)])
#         results_index = numpy.argmax(results)
#         print(results[0]);
#         print(results_index);
#         if results[0][results_index]<0.7:
#             print("do not understand");
#
#         tag = labels[results_index]
#
#         for tg in data["intents"]:
#             if tg['tag'] == tag:
#                 responses = tg['responses']
#
#         print(tag);
#         print(random.choice(responses))
#
# chat()


client = MongoClient("mongodb+srv://shubham024:"+urllib.parse.quote("aman062")+"@cluster0.ujboz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority");
db=client["whatsapp_Db"];
collection=db["users"];
complain=db["complain"];
connectionsdb=db["connectionsdb"];
complaintsdb=db["complaintsdb"];
suggestiondb=db["suggestiondb"];
mobileno=[];
chatdetails=[];
details={
'mobile':"",
'gretted':0,
}
typedept = {
  "1": "Water Department",
  "2": "Electricity Department",
  "3": "LPG indraprastha"
}
def pdetails(num):
    x=connectionsdb.find_one({"mobileno":num});
    text="Your connection id is:"+ str(x["uniqid"]);
    return text;

def msggenerator(cat):
    text="Your request has been transfered to "+typedept[cat] +"\n A technician will be assigned soon.";
    return text;
def tracking(num):
    fi=complaintsdb.find_one({"mobileno":num})
    if fi:
        stt=fi["status"]
        if stt=="todecide":
            return "Your complaint is being sent to administrator for review";
        elif stt=="accept":
            return "your complaint is accepted, a technician will visit soon";
        elif stt=="reject":
            return "sorry , your complaint is reject from admin";
        elif stt=="completed":
            return "you complaint has been solved";
    else:
        return "There is No Complain registered for this number";








app = Flask(__name__)
#root route justto check
@app.route("/")
def hello():
    return "Hello, this is your personal bot!"

@app.route("/sms", methods=['POST'])


def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message


    msg = request.form.get('Body')
    name=request.form.get('ProfileName');
    num=request.form.get("From")
    num=num.replace("whatsapp:","");
    num=num.replace("+","");
    #####

    results = model.predict([bag_of_words(msg, words)])
    results_index = numpy.argmax(results)
    print(results[0]);
    print(results_index);
    flag=False;
    if results[0][results_index]<0.7:
        flag=True;
        print("do not understand");

    tag = labels[results_index]
    respo="hi";
    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']
            print(tag);
            print(random.choice(responses))
            respo=random.choice(responses);



    ###



    numdb=collection.find_one({"number":num});
    resp = MessagingResponse()
    if flag==False and tag in ["thanks","hours","payments"]:
        resp.message(respo);
        return str(resp);
    if (msg.lower()=="bye" or tag=="goodbye" ) and flag==False:
        resp.message(respo);
        collection.update_one({"number":num},{"$set": { "status": "greet" }});
        return str(resp);


    def greeting():
        resp.message(f" Hi ,{name} this is *Adhira* your personal chat Assistant!");


    def suggestion():
        resp.message("How can i Help You ?");
        resp.message("Type 1️⃣ To track complains \n\nType 2️⃣ To create connections\n\nType 3️⃣  To Register Complains \n\nType 4️⃣ To Provide Feedback");
        collection.update_one({"number":num},{"$set": { "status": "suggestion" }});
    if (msg.lower()=="hi" or tag=="greeting" ) and flag==False:
        if numdb!=None and ( numdb["status"]=="new" or numdb["status"]=="addrees" or numdb["status"]=="email") :
            collection.delete_one({"number":num});

        if numdb!=None:
            collection.update_one({"number":num},{"$set": { "status": "greet" }});

    numdb=collection.find_one({"number":num});
    if numdb==None:
        greeting();
        collection.insert_one({"name":name,"status":"new","number":num});
        resp.message(f"It Seems you arr a new User!");
        resp.message("Would you Like to register with us? \n Reply with *yes* or *no*");
    else:
        if numdb["status"]=="new":
            if msg.lower()=="yes":
                collection.update_one({"number":num},{"$set": { "status": "address" }});
                resp.message("Please Enter your Complete adrees");
            elif (msg.lower()=="no"):
                collection.delete_one({"number":num});
                resp.message("Thanks! for giving your time, We can't proceed without registration");
                return str(resp);
            else:
                resp.message("Invalid Input!,Please Reply with *Yes* or *No*");
        elif numdb["status"]=='address':

            if request.form.get('Latitude') and request.form.get('Longitude'):
                ad=completeaddress(request.form.get('Latitude'),request.form.get('Longitude'));
                resp.message("Your addrees is: "+ad);
                collection.update_one({"number":num},{"$set": { "addrees":ad ,"status": "email" }});
            else:
                collection.update_one({"number":num},{"$set": { "addrees":msg ,"status": "email" }});

            resp.message("Please Enter Your Email address");


        elif numdb["status"]=="email":
            collection.update_one({"number":num},{"$set": { "email":msg ,"status": "suggestion" }});
            resp.message("You have been successfully registered");
            suggestion();

        elif numdb["status"]=="suggestion":
            if msg.lower()=="1":
                trc=tracking(num);
                resp.message(trc);
                # comp=complain.find_one({"number":num});
                ##yaha se shuru karna hai
            elif msg.lower()=="2":
                resp.message("Type 1️⃣ for Water Department");
                resp.message("Type 2️⃣ for Electric Department");
                resp.message("Type 3️⃣ for LPG");
                collection.update_one({"number":num},{"$set": { "status": "connection" }});
            elif msg.lower()=="3":
                resp.message("Enter Your Issue");
                collection.update_one({"number":num},{"$set": { "status": "complaint" }});

            elif msg.lower()=="4":
                resp.message("Enter Your Suggestion/ Feedback:");
                collection.update_one({"number":num},{"$set": { "status": "feedback" }});

        elif numdb["status"]=="greet":
            greeting();
            suggestion();
        elif numdb["status"]=="connection":
            connectionsdb.insert_one({"mobileno":num,"dept":tag,"uniqid":random.randint(1000000, 9999999),"status":"todecide"});

            text=msggenerator(msg);
            ptext=pdetails(num);
            resp.message(text);
            resp.message(ptext);
        elif numdb["status"]=="complaint":
            resp.message(tag);
            resp.message(respo);
            complainid=random.randint(1000000, 9999999);
            resp.message("Your complain id is "+str(complainid));
            complaintsdb.insert_one({"mobileno":num,"dept":tag,"uniqid":complainid,"status":"todecide"});
        elif numdb["status"]=="feedback":
            suggestiondb.insert_one({"mobileno":num,"suggestion":msg});
            resp.message("thanks for giving your valuable feedback");






    # resp.message(name);
    # resp.message("You said: {}".format(msg))
    # resp.message(num);
    # if request.form.get('MediaUrl0'):
    #     resp.message(request.form.get('MediaUrl0'));
    # if request.form.get('Latitude') and request.form.get('Longitude'):
    #      resp.message(completeaddress(request.form.get('Latitude'),request.form.get('Longitude')));









    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)

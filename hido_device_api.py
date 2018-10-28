from flask import Flask, jsonify, request
from flask_restful import Api, reqparse
from subprocess import call
import requests
import json
first_app = Flask(__name__)

@first_app.route("/health")
def first_function():
    return jsonify({'status':'success'})

@first_app.route("/barcode/<int:slot_id>", methods=['GET'])
def activate_barcode(slot_id):
    # Instert firmware logic here to activate barcode
    # Logic should fire end barcode results to:
    # POST https://hido-cloud.herokuapp.com/medicine
    # body: { slot_id: number, barcode: string }
    response = call("AT+SCAN=30000")
    URL = "https://hido-cloud.herokuapp.com/medicine"
    params = {'slot_id':slot_id, 'barcode': response}
    requests.post(url = URL, data = params) 
    return jsonify({'response':response, 'slot_id':slot_id})

@first_app.route("/dispense/single", methods=["POST"])
def dispense_single():
    # Dispense single pill firmware goes here.
    # Example of payload is:
    # {"dispense_request":{"id":5,"medicine_id":2,"schedule_id":null,"dispense_at":"2018-10-11T20:06:28.908Z","dispense_quantities_id":null},
    #  "medicine":{"id":2,"name":"Aviane","description":"{21 (Ethinyl Estradiol 0.02 MG / Levonorgestrel 0.1 MG Oral Tablet) / 7 (Inert Ingredients 1 MG Oral Tablet) } Pack [Aviane 28]","slot_id":1,"dosage":"10 mg","state":"active"}}
    parser = reqparse.RequestParser()
    parser.add_argument('schedule', )
    parser.add_argument('medicine')
    args = parser.parse_args()
    quantity = 1
    slot_id = json.loads(args['medicine'])['slot_id']
    response = call("AT+DISPENSE={0},{1}".format(slot_id, quantity))
    return jsonify({'response':response, 'dispense_request':request.json["dispense_request"]})

@first_app.route("/dispense/schedule", methods=["POST"])
def dispense_schedule():
    # Dispense an entire schedule firmware goes here.
    # Example of payload is:
    # {"schedule":{"id":2,"label":"Afternoon","time":"12:30 PM"},
    # "medicine":[
    #    {"dispense":{"id":4,"medicine_id":1,"schedule_id":2,"dispense_at":"2018-10-10T19:35:06.207Z","dispense_quantities_id":null},
    #     "medicine":{"id":1,"name":"Aviane","description":"{21 (Ethinyl Estradiol 0.02 MG / Levonorgestrel 0.1 MG Oral Tablet) / 7 (Inert Ingredients 1 MG Oral Tablet) } Pack [Aviane 28]","slot_id":1,"dosage":"10 mg","state":"inactive"},
    #     "dispense_quantity":{"id":1,"medicine_id":1,"quantity":2,"schedule_id":2}}
    # ]}
    parser = reqparse.RequestParser()
    parser.add_argument('schedule')
    parser.add_argument('medicine')
    args = parser.parse_args()
    for medicine in json.load(args['medicine']):
        quantity = medicine['dispense_quantity']['quantity']
        slot_id = medicine['medicine']['slot_id']
        call("AT+DISPENSE={0},{1}".format(slot_id, quantity))

    return jsonify({'response':'success', 'schedule':request.json["schedule"]})


if __name__ == "__main__":
    first_app.run(host='0.0.0.0')

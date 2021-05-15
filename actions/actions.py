
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import pandas


df_conf = pandas.read_csv('http://api.covid19india.org/states_daily_csv/confirmed.csv')
df_death = pandas.read_csv('https://api.covid19india.org/states_daily_csv/deceased.csv')
df_recovered = pandas.read_csv('https://api.covid19india.org/states_daily_csv/recovered.csv')

# State vs State Code Mapping
statecode_to_state = {"state_mappings":{'tt':'Total','kl':'Kerala', 'dl':'Delhi','tg':'Telangana','rj':'Rajasthan','hr':'Haryana','up':'Uttar Pradesh','la':'Ladakh','tn':'Tamil Nadu','jk':'Jammu and Kashmir','ka':'Karnataka','mh':'Maharashtra','pb':'Punjab','ap':'Andhra Pradesh','ut':'Uttarakhand','or':'Odisha','py':'Puducherry','wb':'West Bengal','ch':'Chandigarh','ct':'Chhattisgarh','gj':'Gujarat','hp':'Himachal Pradesh','mp':'Madhya Pradesh','br':'Bihar','mn':'Manipur','mz':'Mizoram','ga':'Goa','an':'Andaman and Nicobar Islands','jh':'Jharkhand','as':'Assam','ar':'Arunachal Pradesh','tr':'Tripura','ml':'Meghalaya'}}
state_to_statecode = {"state_mappings":{'Total':'tt','Kerala':'kl', 'Delhi':'dl','Telangana':'tg','Rajasthan':'rj','Haryana':'hr','Uttar Pradesh':'up','Ladakh':'la','Tamil Nadu':'tn','Jammu and Kashmir':'jk','Karnataka':'ka','Maharashtra':'mh','Punjab':'pb','Andhra Pradesh':'ap','Uttarakhand':'ut','Odisha':'or','Puducherry':'py','West Bengal':'wb','Chandigarh':'ch','Chhattisgarh':'ct','Gujarat':'gj','Himachal Pradesh':'hp','Madhya Pradesh':'mp','Bihar':'br','Manipur':'mn','Mizoram':'mz','Goa':'ga','Andaman and Nicobar Islands':'an','Jharkhand':'jh','Assam':'as','Arunachal Pradesh':'ar','Tripura':'tr','Meghalaya':'ml'}}


def get_death_count_by_state(state):
    stateval = state.title()
    statecode = (state_to_statecode['state_mappings'][stateval]).upper()
    death_df = df_death[[statecode]].tail(1)
    return death_df[statecode].values[0]

def get_conf_count_by_state(state):
    stateval = state.title()
    statecode = (state_to_statecode['state_mappings'][stateval]).upper()
    conf_df = df_conf[[statecode]].tail(1)
    return conf_df[statecode].values[0]

def get_recovered_count_by_state(state):
    stateval = state.title()
    statecode = (state_to_statecode['state_mappings'][stateval]).upper()
    recovered_df = df_recovered[[statecode]].tail(1)
    return recovered_df[statecode].values[0]



class ActionGreetUser(Action):

    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher, tracker, domain):
        person_name = tracker.get_slot("name")
        if person_name != None:
             dispatcher.utter_message("Hi {}, how can I help you?".format(person_name))
        else:
        	 dispatcher.utter_message(template="utter_what_name")     
        return []

class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message["intent"].get("name")
        name_entity = next(tracker.get_latest_entity_values("name"), None)
        if intent == "enter_data" and name_entity:
            if name_entity and name_entity.lower() != "guru":
                dispatcher.utter_message(template="utter_greet_name", name=name_entity)
                return []
            else:
                dispatcher.utter_message(template="utter_greet_noname")
                return []  
        
        return []        

class Actioncoronastats(Action):

    def name(self) -> Text:
        return "actions_corona_state_stat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        responses = requests.get("https://api.covid19india.org/data.json").json()

        entities = tracker.latest_message['entities']
        state = None

        for i in entities:
            if i["entity"] == "state":
                state = i["value"]

        conf = get_conf_count_by_state(state)
        recov = get_recovered_count_by_state(state)
        death = get_death_count_by_state(state)
        dispatcher.utter_message("Cases in the last 24 hours: {} \n\n Recoveries in the last 24 hours: {} \n\n Deaths in the last 24 hours: {}".format(conf,recov,death))
        if state == "india":
            state = "Total"
        for data in responses["statewise"]:
            if data["state"] == state.title():
            	dispatcher.utter_message("Total Active cases: {} \n\n Total Confirmed cases: {} \n\n Total Recovered cases: {} \n\n Total deaths: {}".format(data["deaths"],data["confirmed"],data["recovered"],data["deaths"]))
        return []
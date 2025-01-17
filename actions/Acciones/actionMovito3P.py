from pickle import FALSE
import string
from tokenize import Double
from typing import Any, Text, Dict, List
from numpy import double, integer
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
import json
import random
import requests
from flask import jsonify
import yaml
from actions.Acciones.actionMotivoPP import habilidad, lenguaje, motivoHabilidadLenuaje
from actions.Acciones.actionVotarPP import diccionarioVotacion, lista_votos, vectorParticipante

matriz_motivos_mencionados = [[0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0]] #5 filas por la cantidad de motivos y 6 columnas por los distintos tipos de optimismo

def motivoVotos(votos) -> string:
    lista_motivos_votos = []
    motivo_votos_1 = f"de la siguiente manera: {votos[0]} en la estimacion optimista, {votos[1]} en la realista y {votos[2]} en la pesimista"
    motivo_votos_2 = f"{votos[0]} en el voto optimista, {votos[1]} en el realista y {votos[2]} en el pesimista como parte de mi evaluacion"
    motivo_votos_3 = f"de la siguiente forma: {votos[0]} en el voto optimista, {votos[1]} en el realista y {votos[2]} en el pesimista"
    motivo_votos_4 = f"{votos[0]} en mi voto optimista, mientras que en el realista {votos[1]} y en el pesimista {votos[2]}"
    motivo_votos_5 = f"{votos[0]} en la estimacion optimista, {votos[1]} en la realista y {votos[2]} en la pesimista como una representacion equilibrada"
    lista_motivos_votos.append(motivo_votos_1)
    lista_motivos_votos.append(motivo_votos_2)
    lista_motivos_votos.append(motivo_votos_3)
    lista_motivos_votos.append(motivo_votos_4)
    lista_motivos_votos.append(motivo_votos_5)
    return random.choice(lista_motivos_votos)

def darMotivo(valor_riesgo, valor_optimismo, nombre_partipante, votos, tarea) -> string:
    votos_menores = lista_votos[0:7]
    motivo = motivoHabilidadLenuaje(habilidad(nombre_partipante), lenguaje(nombre_partipante), votos, valor_riesgo, votos_menores)
    motivo_votos = motivoVotos(votos)
    lista_motivos = []
    print("voto1: " + str(votos[1]))
    print("votos_menores: " + str(votos_menores))
    if (str(votos[1]) in votos_menores): #0,0.5,1,2,3,5,8
        if (valor_optimismo == 5):
            motivo_1 = f"Me considero una persona muy optimista, y {motivo}. Por eso, en la tarea decidi votar {motivo_votos}."
            motivo_2 = f"Decidi votar {motivo_votos}, ya que soy muy optimista y {motivo}"
            motivo_3 = f"Al ser alguien muy optimista, y teniendo en cuenta que {motivo}, he decidido votar {motivo_votos}"
            motivo_4 = f"Mi estimacion es {motivo_votos} ya que {motivo}, ademas ser optimista con el tiempo que nos tomara llevar a cabo la tarea"
            motivo_5 = f"{motivo}. Teniendo en cuenta esto y mi actitud muy optimista, vote {motivo_votos}"
        elif(valor_optimismo == 4):
            motivo_1 = f"Aunque no soy extremadamente optimista, tengo una actitud positiva hacia la tarea. Por eso, he decidido votar {motivo_votos}."
            motivo_2 = f"Incluso siendo moderadamente optimista, he elegido votar {motivo_votos}, ya que veo posibilidades de exito y desafios por igual."
            motivo_3 = f"Aunque mi nivel de optimismo no es maximo, considero que {motivo}. Por lo tanto, he decidido votar {motivo_votos}."
            motivo_4 = f"Siendo optimista en cierta medida y considerando {motivo}, he estimado {motivo_votos}."
            motivo_5 = f"{motivo}. A pesar de no tener un optimismo extremo, he votado {motivo_votos}, manteniendo una perspectiva equilibrada."
        elif(valor_optimismo == 3):
            motivo_1 = f"Me considero una persona muy realista, y {motivo}. Por eso, en la tarea decidi votar {motivo_votos}."
            motivo_2 = f"Al ser extremadamente realista, he decidido votar {motivo_votos}, basandome en un analisis objetivo de la situacion."
            motivo_3 = f"Siendo consciente de la realidad y considerando {motivo}, he votado {motivo_votos} para reflejar mi enfoque pragmatico."
            motivo_4 = f"Dada mi perspectiva altamente realista y teniendo en cuenta {motivo}, he estimado {motivo_votos}."
            motivo_5 = f"{motivo}. Como persona extremadamente realista, he votado {motivo_votos}, considerando todos los posibles escenarios de manera objetiva."
        elif(valor_optimismo == 2):
            motivo_1 = f"No me considero extremadamente realista, ya que tiendo a ser mas optimista en general. Por eso, en esta tarea he decidido votar {motivo_votos}."
            motivo_2 = f"Aunque no soy particularmente realista, tengo una vision mas positiva de la situacion. Por eso, he optado por votar {motivo_votos}."
            motivo_3 = f"No siendo tan realista, he elegido votar {motivo_votos}. Esto refleja mi inclinacion hacia el optimismo en lugar del pesimismo."
            motivo_4 = f"Aunque no me caracterizo por ser muy realista, considerando {motivo}, he estimado {motivo_votos}."
            motivo_5 = f"{motivo}. Siendo consciente de mi tendencia a ser menos realista, he votado {motivo_votos}, manteniendo un enfoque mas positivo en general."
        elif(valor_optimismo == 1):
            motivo_1 = f"Soy consciente de que tiendo a ser un poco pesimista en mi enfoque. Por eso, en esta tarea he decidido votar {motivo_votos}, reflejando mi vision mas cautelosa."
            motivo_2 = f"Siendo una persona con un enfoque mas pesimista, he optado por votar {motivo_votos}, ya que considero importante considerar los posibles desafios y obstaculos."
            motivo_3 = f"Mi inclinacion hacia el pesimismo influye en mi decision. Dado que tiendo a ver los aspectos mas negativos, he votado {motivo_votos}."
            motivo_4 = f"A pesar de no ser extremadamente pesimista, considerando {motivo}, he estimado {motivo_votos}, tomando en cuenta las posibles dificultades."
            motivo_5 = f"{motivo}. Dado mi enfoque mas pesimista, he votado {motivo_votos}, teniendo en cuenta los posibles escenarios adversos."
        elif(valor_optimismo == 0):
            motivo_1 = f"Me considero una persona extremadamente pesimista y siempre espero lo peor. Por eso, en esta tarea he decidido votar {motivo_votos}, ya que veo pocas posibilidades de exito."
            motivo_2 = f"Siendo muy pesimista por naturaleza, he votado {motivo_votos}, ya que considero que los obstaculos y dificultades seran dominantes."
            motivo_3 = f"Mi perspectiva pesimista me lleva a creer que {motivo}. Por lo tanto, he decidido votar {motivo_votos}, reflejando mi vision negativa de la situacion."
            motivo_4 = f"Dada mi mentalidad extremadamente pesimista, considerando {motivo}, he estimado {motivo_votos}, anticipando mayores dificultades."
            motivo_5 = f"{motivo}. Siendo una persona muy pesimista, he votado {motivo_votos}, tomando en cuenta los aspectos mas negativos y desfavorables."
    else:  #13,20,40,100,1000
        if (valor_optimismo == 5):
            motivo_1 = f"Aunque mi nivel de optimismo es alto, he considerado los desafios y obstaculos al votar {motivo_votos}."
            motivo_2 = f"Incluso siendo optimista, he tenido en cuenta los posibles problemas y he votado {motivo_votos}."
            motivo_3 = f"A pesar de mi enfoque optimista, he votado {motivo_votos} para reflejar una evaluacion equilibrada de la situacion."
            motivo_4 = f"Siendo una persona con una perspectiva optimista, he estimado {motivo_votos}, considerando los desafios que podrian surgir."
            motivo_5 = f"A pesar de mi actitud optimista, he votado {motivo_votos} debido a los posibles obstaculos y dificultades."
        elif(valor_optimismo == 4):
            motivo_1 = f"Incluso siendo moderadamente optimista, he considerado los posibles desafios y he votado {motivo_votos}."
            motivo_2 = f"Aunque mi nivel de optimismo no es maximo, he tomado en cuenta tanto las posibilidades de exito como los desafios al votar {motivo_votos}."
            motivo_3 = f"Dado que mi optimismo es moderado y considerando {motivo}, he estimado {motivo_votos} para reflejar una perspectiva equilibrada."
            motivo_4 = f"A pesar de no ser extremadamente optimista, he votado {motivo_votos}, teniendo en cuenta tanto los aspectos positivos como los posibles obstaculos."
            motivo_5 = f"{motivo}. Siendo moderadamente optimista, he votado {motivo_votos}, manteniendo una perspectiva equilibrada."
        elif(valor_optimismo == 3):
            motivo_1 = f"Aunque tiendo a ser optimista, he tenido en cuenta los aspectos realistas y he votado {motivo_votos}."
            motivo_2 = f"Incluso siendo moderadamente optimista, he considerado los posibles contratiempos y he votado {motivo_votos}."
            motivo_3 = f"Dado mi enfoque realista con toques de optimismo, he estimado {motivo_votos} para reflejar una vision equilibrada de la situacion."
            motivo_4 = f"Siendo alguien con una perspectiva realista pero tambien optimista, he votado {motivo_votos}, considerando los desafios que podrian presentarse."
            motivo_5 = f"Considerando mi enfoque optimista en combinacion con una vision realista, he votado {motivo_votos} debido a los posibles obstaculos y dificultades."
        elif(valor_optimismo == 2):
            motivo_1 = f"Incluso no siendo particularmente optimista, he tenido en cuenta los posibles desafios y he votado {motivo_votos}."
            motivo_2 = f"Aunque mi enfoque tiende a ser mas optimista, he considerado los posibles obstaculos y he votado {motivo_votos}."
            motivo_3 = f"Dado que no soy tan optimista, he estimado {motivo_votos} para reflejar una perspectiva mas cautelosa."
            motivo_4 = f"A pesar de no ser extremadamente optimista, considerando {motivo}, he votado {motivo_votos}, tomando en cuenta los posibles desafios."
            motivo_5 = f"{motivo}. Siendo moderadamente optimista, he votado {motivo_votos}, manteniendo una perspectiva mas equilibrada."
        elif(valor_optimismo == 1):
            motivo_1 = f"Siendo consciente de que tiendo a ser un poco pesimista en mi enfoque, he considerado los posibles desafios y he votado {motivo_votos}."
            motivo_2 = f"Considerando mi enfoque mas pesimista, he tenido en cuenta los posibles obstaculos y he votado {motivo_votos}."
            motivo_3 = f"Dado mi enfoque mas cauteloso, he estimado {motivo_votos}, tomando en cuenta los posibles desafios y dificultades."
            motivo_4 = f"A pesar de no ser extremadamente pesimista, considerando {motivo}, he votado {motivo_votos}, anticipando posibles dificultades."
            motivo_5 = f"{motivo}. Siendo una persona mas pesimista, he votado {motivo_votos}, considerando los posibles obstaculos y desafios."
        elif(valor_optimismo == 0):
            motivo_1 = f"Dado que soy extremadamente pesimista, he evaluado los posibles desafios y he votado {motivo_votos}."
            motivo_2 = f"Siendo muy pesimista, he tenido en cuenta los posibles obstaculos y he votado {motivo_votos}."
            motivo_3 = f"Asumiendo una perspectiva altamente pesimista, he estimado {motivo_votos}, considerando los desafios que podrian surgir."
            motivo_4 = f"Siendo una persona con un enfoque muy pesimista, he votado {motivo_votos}, anticipando dificultades y obstaculos."
            motivo_5 = f"{motivo}. Siendo extremadamente pesimista, he votado {motivo_votos}, considerando los posibles desafios y dificultades."
    #La proxima logica se hace para que no se repitan los motivos en una misma ceremonia. Si todos estan dichos, pueden repetirse.
    for i in range(len(matriz_motivos_mencionados)):
        if matriz_motivos_mencionados[i][valor_optimismo] == 0:
            lista_motivos.append(eval(f"motivo_{i+1}"))
    if len(lista_motivos) == 0: #Todos los motivos fueron utilizados.
        lista_motivos.append(motivo_1)
        lista_motivos.append(motivo_2)
        lista_motivos.append(motivo_3)
        lista_motivos.append(motivo_4)
        lista_motivos.append(motivo_5)
    posicion_motivo_final, motivo_final = random.choice(list(enumerate(lista_motivos)))
    matriz_motivos_mencionados[posicion_motivo_final][valor_optimismo] = 1
    return motivo_final

class ActionMotivoEstimacion3Puntos(Action):
    def name(self) -> Text:
        return "action_motivo_estimacion_3_puntos"
    
    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #nombre_participante = str(tracker.get_slot("participante"))
        nombre_participante = str(tracker.sender_id)
        message = "Vote eso ya que no sabia que votar" #default
        votos = (5,8,13) #Votos default. El primer voto es optimista, luego realistas y por ultimo pesimista
        tarea = ""
        if (nombre_participante != None):
            vector_participante = vectorParticipante(nombre_participante)
            if(vector_participante != None):
                if (diccionarioVotacion[nombre_participante]["Voto"] != []): #Consulto si tiene un valor en la primera votacion
                    votos = diccionarioVotacion[nombre_participante]["Voto3puntos"][len(diccionarioVotacion[nombre_participante]["Voto3puntos"])-1]
                    print("Voto estimacion 3 p: " + str(votos))
                if (diccionarioVotacion[nombre_participante]["Tarea"] != []):
                    tarea = diccionarioVotacion[nombre_participante]["Tarea"][len(diccionarioVotacion[nombre_participante]["Tarea"])-1]
                    print("Tarea: " + str(tarea))
                valor_riesgo = vector_participante["riesgo"]
                valor_optimismo = vector_participante["optimismo"]
                if (valor_optimismo != "" and votos != "" and tarea != ""):
                    message = darMotivo(valor_riesgo, valor_optimismo, nombre_participante, votos, tarea)
        dispatcher.utter_message(text=message)
        return []
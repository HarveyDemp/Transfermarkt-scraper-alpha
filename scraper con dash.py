import dash
from dash import ctx
from dash.dependencies import Input, Output


import dash_core_components as dcc
import dash_html_components as html
from bs4 import BeautifulSoup
from urllib.request import urlopen,Request
import pandas as pd
import time

app = dash.Dash(__name__)


     

app.layout = html.Div(
    children=[
    html.H1(children="Transfermarkt Scraper"),
    html.P(
    children=(dcc.Input(id="squadra",
        placeholder="Inserisci l'url della squadra",
        type="url",
        style={"align":"center"}),
    html.Br(),
    html.Br(),
    html.Button("Submit",id="btn-nclicks-1",n_clicks=0),
    html.Button("Cancel",id="btn-nclicks-2",n_clicks=0))),
    dcc.Download(id="download-team-csv"),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.P(children=(dcc.Loading(
            id="loading-1",
            type="circle",
            children=html.Div(id="loading-output-1"))),
        style={"align":"center","padding-left": '-20'})
    ])

def tec_stats(link,n_comp=1):
    req=Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as fp:
        soup=BeautifulSoup(fp,"html.parser")
    competizioni=soup.find_all("tbody")
    result=pd.DataFrame(columns=["Competizione","Presenze","Gol","Assist","Cartellini Gialli",
                              "Doppi Gialli","Cartellini Rossi","Minuti Giocati"])
    competizioni=competizioni[1].find_all("tr")
    if n_comp==0 :
        for i in range(len(competizioni)):
            competizione=competizioni[i].find_all("td")
            lista=list()
            for j in range(1,len(competizione)):
                lista.append(competizione[j].string)
                lista=pd.DataFrame([{"Competizione":lista[0],"Presenze":lista[1],"Gol":lista[2],
                                     "Assist":lista[3],"Cartellini Gialli":lista[4],
                                     "Doppi Gialli":lista[5],"Cartellini Rossi":lista[6],
                                     "Minuti Giocati":lista[7]}])
            result=pd.concat([result,lista])
        return result.iloc[0]
    totale=soup.find_all("tfoot")[0]
    totale=totale.find_all("td")
    lista=list()
    for i in range(2,len(totale)):
        if totale[i].string == "-":lista.append(0)
        else:lista.append(totale[i].string)
    return lista

@app.callback(Output( "download-team-csv","data"),
              Output("loading-output-1", "children"),
              Input("btn-nclicks-1", "n_clicks"),  
              Input("btn-nclicks-2", "n_clicks"),
              Input("squadra","value"))

def scraping(btn1,btn2,value):
    if "btn-nclicks-1" == ctx.triggered_id:
        req=Request(value, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as fp:
            soup=BeautifulSoup(fp,"html.parser")    
        time.sleep(10)
        team=pd.DataFrame(columns=["Numero di Maglia","Ruolo","Nome","Nasc./Età","Nazionalità",
                                       "Presenze","Gol","Assist","Cartellini Gialli",
                                       "Doppi Gialli","Cartellini Rossi","Minuti Giocati"])
        all_players=soup.find_all("tbody")[1]
        len_rosa=len(all_players.find_all("tr",class_="even"))+len(all_players.find_all("tr",class_="odd"))
        player=all_players.find("tr")
        for i in range(len_rosa):
               features=player.find_all("td")
               lista=list()
               for j in range(len(features)):
                   lista.append(features[j].string)
                   while None in lista:
                       lista.remove(None)
               lista.append(player.find("img",class_="flaggenrahmen")["alt"])
               link="https://www.transfermarkt.it" + player.find("td",class_="hauptlink").find("a",href=True)["href"]
               link=link.replace("profil","leistungsdaten")
               lista.extend(tec_stats(link=link))
               if lista[1]=="Portiere": 
                   lista=pd.DataFrame([{"Numero di Maglia":lista[0],"Ruolo":lista[1],"Nome":lista[2],
                                                "Nasc./Età":lista[3],"Nazionalità":lista[4],"Presenze":lista[5],
                                                "Gol":lista[6],"Assist": "NA","Cartellini Gialli":lista[7],
                                                "Doppi Gialli":lista[8],"Cartellini Rossi":lista[9],
                                                "Minuti Giocati":lista[12]}])
                   team=pd.concat([team,lista])
               else:
                   lista=pd.DataFrame([{"Numero di Maglia":lista[0],"Ruolo":lista[1],"Nome":lista[2],
                                               "Nasc./Età":lista[3],"Nazionalità":lista[4],"Presenze":lista[5],
                                               "Gol":lista[6],"Assist": lista[7],"Cartellini Gialli":lista[8],
                                               "Doppi Gialli":lista[9],"Cartellini Rossi":lista[10],
                                               "Minuti Giocati":lista[11]}])
                   print(lista)
                   team=pd.concat([team,lista])
               time.sleep(10)
               player=player.next_sibling.next_sibling
               if "btn-nclicks-2"== ctx.triggered_id: break
        team=team.set_index(["Numero di Maglia"])
        return dcc.send_data_frame(team.to_csv, "team.csv")
    


if __name__ == "__main__":
    app.run_server()

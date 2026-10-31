# Ice Hockey ML Project

Referência rápida com informações sobre as bases de dados

---

## 1. Estrutura da Base de Dados (Tabelas)

### Jogadores e Treinadores
* **Master:** Detalhes biográficos e atributos de carreira de todos os jogadores e treinadores

* **Scoring:** Métricas de desempenho dos jogadores

* **Goalies:** Métricas de desempenho dos guarda-redes

* **Coaches:** Estatísticas de treino

* **ScoringShootout / GoaliesShootout:** Métricas de desempenho individual e de guarda-redes, respetivamente, em situações de desempate por penáltis

* **ScoringSup:** Estatísticas suplementares de pontuação

### Equipas e Época Regular
* **Teams:** Dados da época, classificações, estatísticas de golos e estatuto de qualificação para os playoffs

* **TeamsHalf:** Classificações da primeira e segunda metades da época

* **TeamSplits:** Métricas de desempenho da equipa em casa/fora 

* **TeamVsTeam:** Registos de confrontos diretos entre equipas

* **CombinedShutouts:** Registos de *shutouts* combinados, indicando a equipa, o adversário e os guarda-redes envolvidos

### Playoffs e Finais (Stanley Cup)
* **SeriesPost:** Registos de resultados 

* **TeamsPost / ScoringSC / GoaliesSC / TeamsSC:** Estatísticas de desempenho de equipas nos playoffs, e de jogadores, guarda-redes e equipas nas finais da Stanley Cup

### Prémios e Informação Adicional
* **AwardsPlayers / AwardsCoaches / AwardsMisc:** Prémios, troféus e equipas *all-star* da pós-temporada para jogadores, treinadores e categorias diversas

* **HOF:** Informação sobre o *Hall of Fame*

* **abbrev:** Abreviaturas utilizadas nas tabelas *Teams* e *SeriesPost*


---

## 2. Glossário de Variáveis

### Identificadores (IDs)
* **playerID / coachID / hofID:** IDs do Jogador, Treinador e Hall of Fame

* **tmID / franchID:** ID da Equipa e ID do Franchising

* **lgID / confID / divID:** IDs da Liga, Conferência e Divisão

* **legendsID / ihdbID / hrefID:** IDs externos nos sites Legends Of Hockey, Internet Hockey Database e Hockey-Reference.com

### Características Biográficas e de Jogo
* **firstNHL:** Primeira época na NHL (epoca 2005-06 apareçe como 2005)

* **shootCatch:** Mão de remate (ou mão de receção para os guarda-redes)

* **pos:** Posição do jogador

* **stint:** Ordem de aparição numa determinada época

### Métricas de Desempenho e Resultados
**"G":** Geralmente significa **Golos marcados** (*Goals scored*), **EXCETO** nas tabelas **Coaches**, **Teams**, **TeamsHalf**, **TeamsPost** e **TeamsSC**, onde significa **Jogos disputados** (*Games*)

* **GP:** Jogos disputados (*Games played*)
* **A:** Assistências
* **Pts:** Pontos
* **W / L:** Vitórias / Derrotas
* **T/OL:** Empates / Derrotas no prolongamento (*Overtime losses*)
* **OTL:** Derrotas no prolongamento
* **hW / rW:** Vitórias em casa / Vitórias fora
* **JanW / JanL / JanT / JanOL:** Vitórias, derrotas, empates e derrotas no prolongamento referentes ao mês de Janeiro

* **R/P:** "R" para indicar época regular, ou "P" para pós-temporada

### Métricas de Acontecimentos Específicos
* **PIM:** Minutos de penalização (*Penalty minutes*)
* **PPG / PPA:** Golos e Assistências em *Power play* (vantagem numérica)
* **SHG / SHA:** Golos e Assistências em situação *Short-handed* (desvantagem numérica)
* **SHF:** Golos *Shorthanded* a favor
* **ENG:** Golos de baliza aberta (*Empty net goals*)
* **GDG:** Golos decisivos (*Game-deciding goals*)
* **SoW / SoL:** Vitórias e Derrotas em *Shootouts* (penáltis)

### Métricas Defensivas e de Guarda-Redes
* **GA / SA:** Golos sofridos (*Goals against*) / Remates sofridos (*Shots against*)
* **S:** Remates (*Shots*)
* **SHO:** *Shutouts* (jogos sem sofrer golos)


# Para ativar venv:
source .venv/bin/activate

## Previsão da classificação final

Gere primeiro as estatísticas agregadas por equipa a partir dos dados dos
jogadores e, em seguida, treine o modelo de previsão do lugar final na época
regular. O modelo usa as estatísticas das até três épocas anteriores da mesma
franquia. A avaliação usa walk-forward em todas as épocas com histórico
anterior disponível: cada época é prevista por um modelo treinado apenas com
épocas anteriores. O modelo final é treinado com todas as épocas disponíveis.
As previsões são ordenadas para mostrar a posição na liga e dentro da divisão.

```powershell
python -m pip install -r requirements.txt
python hockey_development_data\curate_player_stats.py
```

Abra `hockey_development_data\train_team_rank_model.ipynb` no Jupyter ou VS Code
e execute as células pela ordem apresentada. O notebook mostra o erro médio
absoluto e duas métricas de exatidão do rank da divisão — posição exata e
posição com tolerância de ±1 — na avaliação walk-forward. Exporta a
tabela completa para `hockey_development_data\team_rank_validation_results.csv`
e o resumo das métricas para
`hockey_development_data\team_rank_validation_metrics.csv`. O modelo final fica
na variável `final_model` do kernel.
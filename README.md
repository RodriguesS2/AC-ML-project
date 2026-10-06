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
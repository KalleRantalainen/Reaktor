# Ratkaisu Reaktorin ennakkotehtävään
Ohjelma päivittää tietoja sivulle: https://nodronezone.pablospowder.repl.co/
Ohjelmaa pyöritetään Replitin palvelimilla ja sivustoa kutsutaan myös uptime robotin avulla, jotta Replit ei luule sivua käyttämättömäksi ja lopeta ohjelman suorittamista.
Ratkaisussa tiedonhaku netistä ja sen prosessointi on tehty Pythonilla. Tietoa haetaan 2 sekunnin välein, joten nettisivu päivittyy noin kahden sekunnin välein.
Tieto päivitetään ensin json muotoiseen tiedostoon, josta se muunnetaan pythonilla html muotoiseksi ja tämä html tiedosto taas toimii nettisivun pohjana.
Tiedostoissa on tarkempi kuvaus koskien eri funktioita ja tiedostojen käyttötarkoitusta pois lukien tiedostot pilot_information.json ja information.html, jotka ovat
tuotu repositorioon lähinnä esimerkkinä siitä minkälaisilta ne voisivat näyttää. Todellisuudessa näiden kahden tiedoston sisältöä päivitetään 2 sekunnin välein, sillä
uusia droneja saapuu NDZ:lle ja osa lentäjistä ei ole rikkonut lentokieltoa 10 minuuttiin, jolloin tiedot poistetaan.
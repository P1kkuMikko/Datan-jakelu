"""
FastAPI First Steps & Tutorial -sovellus
Tämä sovellus esittelee FastAPI-tutoriaalin keskeiset käsitteet datan jakelussa:
1. Perusreitti (GET /) - First Steps
2. Polkuparametrit ja tyyppitarkistukset (GET /items/{item_id})
3. Kyselyparametrit ja datan suodatus (GET /countries)
4. Pydantic-tietomallit ja uuden datan lähetys (POST /countries)
5. Automaattinen interaktiivinen API-dokumentaatio (/docs ja /redoc)
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# 1. Alustetaan FastAPI-sovellus metatiedoilla (näkyvät /docs -näkymässä)
app = FastAPI(
    title="Datan jakelun harjoitus-API (FastAPI)",
    description="FastAPI-tutoriaalin pohjalta rakennettu rajapintasovellus, joka jakelee maakohtaista tilastodataa.",
    version="1.0.0"
)


# 2. Määritellään Pydantic-malli (skeema) datan validoimiseksi ja dokumentoimiseksi
class CountryStats(BaseModel):
    country: str = Field(..., examples=["Finland"], description="Maan nimi")
    continent: str = Field(..., examples=["Europe"], description="Maanosa")
    life_exp: float = Field(..., gt=0, examples=[81.8], description="Eliniänodote vuosina")
    gdp_per_cap: float = Field(..., gt=0, examples=[49000.0], description="BKT asukasta kohden (USD)")


# Esimerkkidata muistissa (simuloi tietokantaa tai ladattua aineistoa)
COUNTRIES_DB: list[CountryStats] = [
    CountryStats(country="Finland", continent="Europe", life_exp=79.3, gdp_per_cap=33207.0),
    CountryStats(country="Sweden", continent="Europe", life_exp=80.9, gdp_per_cap=33859.0),
    CountryStats(country="Japan", continent="Asia", life_exp=82.6, gdp_per_cap=31656.0),
    CountryStats(country="Canada", continent="Americas", life_exp=80.7, gdp_per_cap=36319.0),
    CountryStats(country="New Zealand", continent="Oceania", life_exp=80.2, gdp_per_cap=25185.0),
]


# --- VAIHE 1: First Steps (Perusreitti) ---
@app.get("/", tags=["Perusreitit"])
async def root():
    """
    FastAPI-tutoriaalin ensimmäinen askel (First Steps):
    Palauttaa yksinkertaisen JSON-viestin. FastAPI muuntaa Pythonin sanakirjan (dict)
    automaattisesti JSON-muotoon.
    """
    return {
        "message": "Hello World! Tervetuloa FastAPI-rajapintaan.",
        "docs_url": "Avaa /docs selaimessa kokeillaksesi interaktiivista Swagger UI -dokumentaatiota!"
    }


# --- VAIHE 2: Polku- ja kyselyparametrit + tyyppivihjeet ---
@app.get("/items/{item_id}", tags=["Perusreitit"])
async def read_item(item_id: int, q: Optional[str] = None):
    """
    Esittelee polkuparametrin (`item_id: int`) ja valinnaisen kyselyparametrin (`q`).
    Jos `item_id` ei ole kokonaisluku (esim. `/items/abc`), FastAPI palauttaa automaattisesti
    selkeän 422 Unprocessable Entity -virheen.
    """
    return {"item_id": item_id, "q": q}


# --- VAIHE 3: Datan jakelu rajapinnan yli suodatuksella ---
@app.get("/countries", response_model=list[CountryStats], tags=["Tilastodata"])
async def get_countries(
    continent: Optional[str] = Query(default=None, description="Suodata maanosan mukaan (esim. Europe tai Asia)"),
    min_life_exp: Optional[float] = Query(default=None, description="Rajaa pienin eliniänodote")
):
    """
    Palauttaa listan maista JSON-muodossa. Tukee kyselyparametreilla suodattamista.
    """
    results = COUNTRIES_DB
    if continent:
        results = [c for c in results if c.continent.lower() == continent.lower()]
    if min_life_exp is not None:
        results = [c for c in results if c.life_exp >= min_life_exp]
    return results


# --- VAIHE 4: Yksittäisen maan haku polkuparametrilla ---
@app.get("/countries/{country_name}", response_model=CountryStats, tags=["Tilastodata"])
async def get_country_by_name(country_name: str):
    """
    Hakee yksittäisen maan tiedot nimen perusteella tai palauttaa 404-virheen, jos maata ei löydy.
    """
    for c in COUNTRIES_DB:
        if c.country.lower() == country_name.lower():
            return c
    raise HTTPException(status_code=404, detail=f"Maata '{country_name}' ei löytynyt aineistosta.")


# --- VAIHE 5: Uuden datan lisääminen (POST + Pydantic-validointi) ---
@app.post("/countries", response_model=CountryStats, status_code=201, tags=["Tilastodata"])
async def add_country(new_country: CountryStats):
    """
    Vastaanottaa JSON-pyynnön, validoi sen `CountryStats`-mallin avulla ja lisää sen listaan.
    """
    COUNTRIES_DB.append(new_country)
    return new_country

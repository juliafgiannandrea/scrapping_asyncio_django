from ninja import Router
from typing import List
from webscrapping.schemas import ImovelIn, ImovelOut, FiltroScraping
from webscrapping import views
from webscrapping.models import Imoveis
from django.forms.models import model_to_dict
import asyncio
from pathlib import Path
import json

router = Router()

@router.post("/salvar-dados")
async def salvar_dados(request, dados: List[ImovelIn]):
    return await views.salvar_dados(request, dados)

@router.post("/exportar-excel")
async def exportar_excel(request, dados: List[ImovelIn]):
    return await views.exportar_excel(request, dados)

@router.get("/imoveis", response=List[ImovelOut])
async def listar_imoveis(request):
    return await views.listar_imoveis(request)


@router.post("/executar-scraping")
async def iniciar_scraping(request, filtros: FiltroScraping):
    asyncio.create_task(views.executar_scraping_e_retornar(filtros))
    return {"mensagem": "Scraping iniciado em segundo plano."}


@router.get("/resultados-atuais")
def obter_resultados_atuais(request):
    from pathlib import Path
    import json
    import tempfile

    caminho = Path(tempfile.gettempdir()) / "resultados_scraping.json"
    if caminho.exists():
        with caminho.open(encoding="utf-8") as f:
            return json.load(f)
    return []
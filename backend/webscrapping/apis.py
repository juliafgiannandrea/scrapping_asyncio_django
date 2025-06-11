from ninja import Router
from typing import List
from webscrapping.schemas import ImovelIn, ImovelOut, FiltroScraping
from webscrapping import views
import asyncio
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


# @router.post("/executar-scraping")
# async def iniciar_scraping(request, filtros: FiltroScraping):
#     asyncio.create_task(views.executar_scraping_em_background(filtros))
#     return {"mensagem": "Scraping iniciado em segundo plano."}



#para exibir o resultado na tela 
@router.post("/executar-e-retornar")
async def executar_scraping_e_retornar(request, filtros: FiltroScraping):
    return await views.executar_scraping_e_retornar(filtros)



import uuid
@router.post("/iniciar-tarefa")
async def iniciar_tarefa(request, filtros: FiltroScraping):
    task_id = str(uuid.uuid4())
    await views.executar_scraping_em_background(filtros, task_id)
    return {"task_id": task_id}


@router.get("/resultado-tarefa/{task_id}")
def resultado_tarefa(request, task_id: str):
    dados = views.resultados_temp.get(task_id)
    if dados is None:
        return {"status": "pending", "dados": []}
    return {"status": "done", "dados": dados}

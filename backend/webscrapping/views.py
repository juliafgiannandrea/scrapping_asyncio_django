import asyncio
import pandas as pd
from django.utils.timezone import now
from webscrapping.models import Imoveis
from webscrapping.schemas import ImovelIn, FiltroScraping
from asgiref.sync import sync_to_async
from pathlib import Path
from webscrapping.scraping.navegador import iniciar_navegador
from webscrapping.scraping.extrator import extrair_dados
from webscrapping.scraping.tratamento import tratar_dataframe
from webscrapping.scraping.filtros import aplicar_filtros
from django.http import JsonResponse



@sync_to_async
def salvar_no_banco_async(dados):
    novos = 0
    for item in dados:
        if not Imoveis.objects.filter(link=item.link).exists():
            Imoveis.objects.create(**item.dict(), data_extracao=now())
            novos += 1
    return novos

@sync_to_async
def exportar_excel_async(dados):
    df = pd.DataFrame([item.dict() for item in dados])
    path = Path("data")
    path.mkdir(exist_ok=True)
    filename = path / f"imoveis_{now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    df.to_excel(filename, index=False)
    return str(filename)


async def salvar_dados(request, dados: list[ImovelIn]):
    novos = await salvar_no_banco_async(dados)
    if novos == 0:
        return {"mensagem": "Imóveis já cadastrados."}
    else:
        return {"mensagem": f"{novos} registros salvos com sucesso."}

async def exportar_excel(request, dados: list[ImovelIn]):
    path = await exportar_excel_async(dados)
    return {"mensagem": "Arquivo Excel exportado com sucesso.", "arquivo": path}



@sync_to_async
def listar_todos_async():
    return list(Imoveis.objects.all().values())

async def listar_imoveis(request):
    dados = await listar_todos_async()
    return JsonResponse(dados, safe=False)


#para exibir os resultados da busca no front na hora 
async def executar_scraping_e_retornar(filtros: FiltroScraping):
    driver = iniciar_navegador(headless=True)
    try:
        aplicar_filtros(driver, **filtros.dict())
        df = extrair_dados(driver)
        dados = tratar_dataframe(df).to_dict(orient="records")    

        return dados  # <-- aqui está o retorno direto dos dados da busca
    except Exception as e:
        print(f"Erro ao executar scraping: {e}")
        return []
    finally:
        driver.quit()





import uuid

resultados_temp = {}  # DICIONÁRIO EM MEMÓRIA TEMPORÁRIO

async def executar_scraping_em_background(filtros: FiltroScraping, task_id: str):
    def tarefa():
        try:
            driver = iniciar_navegador(headless=True)
            aplicar_filtros(driver, **filtros.dict())
            df = extrair_dados(driver)
            dados = tratar_dataframe(df).to_dict(orient="records")
            resultados_temp[task_id] = dados
        except Exception as e:
            print(f"Erro no scraping: {e}")
            resultados_temp[task_id] = []
        finally:
            driver.quit()

    asyncio.create_task(asyncio.to_thread(tarefa))

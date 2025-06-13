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
import requests 
import json
import tempfile

# @sync_to_async
# def salvar_no_banco_async(dados):
#     novos = 0
#     for item in dados:
#         if Imoveis.objects.filter(link=item.link).exists():
#             Imoveis.objects.create(**item.dict(), data_extracao=now())
#             novos += 1
#     return novos

async def salvar_dados(request, dados: list[ImovelIn]):
    novos = await salvar_no_banco_async(dados)
    if novos == 0:
        return {"mensagem": "Imóveis já cadastrados."}
    else:
        return {"mensagem": f"{novos} registros salvos com sucesso."}


@sync_to_async
def salvar_no_banco_async(dados):
    novos = 0
    for item in dados:
        # Converte para dicionário
        dados_dict = item.dict()

        # Verifica se todos os campos (exceto o link) são "N/A" ou vazios
        somente_na = all(
            valor in ["N/A", None, ""] for chave, valor in dados_dict.items() if chave != "link"
        )

        # Se TODOS os campos (exceto o link) forem N/A, ignora
        if somente_na:
            continue

        # Se passou na verificação, salva normalmente
        if not Imoveis.objects.filter(link=item.link).exists():
            Imoveis.objects.create(**dados_dict, data_extracao=now())
            novos += 1

    return novos






@sync_to_async
def listar_todos_async():
    return list(Imoveis.objects.all().values())

async def listar_imoveis(request):
    dados = await listar_todos_async()
    return JsonResponse(dados, safe=False)


ARQUIVO_RESULTADOS = Path(tempfile.gettempdir()) / "resultados_scraping.json"

async def executar_scraping_e_retornar(filtros: FiltroScraping):
    ARQUIVO_RESULTADOS.write_text("[]", encoding="utf-8") #para apagar resultados de busca anteriores 
    driver = iniciar_navegador(headless=True)
    try:
        aplicar_filtros(driver, **filtros.dict())
        df = extrair_dados(driver)
        dados = tratar_dataframe(df).to_dict(orient="records")

        # salvar os resultados no arquivo temporário
        ARQUIVO_RESULTADOS.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        return dados
    except Exception as e:
        print(f"Erro ao executar scraping: {e}")
        return []
    finally:
        driver.quit()



from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_voyageai import VoyageAIEmbeddings, VoyageAIRerank
from langchain_community.embeddings import JinaEmbeddings
from langchain_community.document_compressors import JinaRerank
from langchain_together.chat_models import ChatTogether
from langchain_together.embeddings import TogetherEmbeddings

import requests
import numpy as np
from filelock import Timeout, FileLock

from typing import Any
from collections import OrderedDict
import json
import datetime
import time
import os
import json

def load_json_config_file(name : str):
    return json.load(open(
        os.path.dirname(__file__) + f"/../../resources/{name}.json", 
        "r", encoding = "utf-8"
    ))

def save_json_config_file(name : str, data):
    json.dump(
        data,
        open(
            os.path.dirname(__file__) + f"/../../resources/{name}.json", 
            "w", encoding = "utf-8"
        ),
        ensure_ascii = False, 
        indent = 4
    )

def get_filelock(name : str):
    return FileLock(os.path.dirname(__file__) + f"/../../resources/locks/{name}.lock")

def get_provider_and_model(data : str) -> tuple[str, str]:
    """Takes in the model string name and divides into provider name and model name"""
    data = data.split(" - ")
    if len(data) != 2:
        return "None", "None"
    return data[0], data[1]

def get_text_token_len(data : str) -> int:
    return len(data) // 4

def add_model_usage(
        logName: str | None, 
        modelType: str, 
        modelName: str, 
        inUsage: int,
        outUsage: int,
    ):
    """Adds the given token usage to the log"""

    if logName is None:
        return
    datem = datetime.datetime.today().strftime("%Y-%m")
    
    with get_filelock("usage"):
        usage = load_json_config_file(logName)

        if datem not in usage:
            usage[datem] = {}
        if modelType not in usage[datem]:
            usage[datem][modelType] = {}
        if modelName not in usage[datem][modelType]:
            usage[datem][modelType][modelName] = { "in": 0, "out": 0 }

        usage[datem][modelType][modelName]["in"] += inUsage
        usage[datem][modelType][modelName]["out"] += outUsage

        save_json_config_file(logName, usage)
 
class LRUCache:
 
    # initialising capacity
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
 
    # we return the value of the key
    # that is queried in O(1) and return -1 if we
    # don't find the key in out dict / cache.
    # And also move the key to the end
    # to show that it was recently used.
    def get(self, key: str) -> Any:
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]
 
    # first, we add / update the key by conventional methods.
    # And also move the key to the end to show that it was recently used.
    # But here we will also check whether the length of our
    # ordered dictionary has exceeded our capacity,
    # If so we remove the first key (least recently used)
    def put(self, key: str, value: Any) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last = False)

class CustomDenseEmbeddings:

    def __init__(this, host : str, modelName : str):
        this.url = host + "/embed_dense"
        this.modelName = modelName

    def embed_internal(
            this, 
            texts: list[str], 
            isQuery: bool
        ):

        return requests.get(
            this.url, 
            json = {
                "data": texts,
                "model": this.modelName,
                "isQuery": isQuery
            }
        ).json()

    def embed_documents(this, texts: list[str]) -> list[list[float]]:
        return this.embed_internal(texts, False)
    
    def embed_document(this, doc: str) -> list[float]:
        return this.embed_internal([doc], False)[0]
    
    def embed_queries(this, texts: list[str]) -> list[list[float]]:
        return this.embed_internal(texts, True)

    def embed_query(this, query: str) -> list[float]:
        return this.embed_internal([query], True)[0]
    
class NoneDenseEmbeddings:
    """Returns empty dense embeddings"""
    def __init__(this): pass
    def embed_documents(this, texts: list[str]) -> list[list[float]]: return [[0] for t in texts]
    def embed_document(this, doc: str) -> list[float]: return [0]
    def embed_queries(this, texts: list[str]) -> list[list[float]]: return [[0] for t in texts]
    def embed_query(this, query: str) -> list[float]: return [0]

class DenseEmbeddingsDispatcher:

    def __init__(this, modelName : str, cacheSize : int, **kwargs):
        this.docCache = LRUCache(cacheSize)
        this.queryCache = LRUCache(cacheSize)
        this.modelName = modelName
        this.usageLogName = kwargs.get("usage_log_name", None)

        embedProvider, embedModel = get_provider_and_model(modelName)
        if embedProvider == "Ollama":
            this.model = OllamaEmbeddings(
                base_url = kwargs["ollama_host"], 
                model = embedModel, 
            )
        elif embedProvider == "Google":
            this.model = GoogleGenerativeAIEmbeddings(
                model = embedModel,
                google_api_key = kwargs["google_api_key"],
            )
        elif embedProvider == "OpenAI":
            this.model = OpenAIEmbeddings(
                api_key = kwargs["openai_api_key"],
                model = embedModel,
            )
        elif embedProvider == "Jina":
            this.model = JinaEmbeddings(
                jina_api_key = kwargs["jina_api_key"],
                model_name = embedModel
            )
        elif embedProvider == "Together":
            this.model = TogetherEmbeddings(
                model = embedModel,
                api_key = kwargs["together_api_key"],
            )
        elif embedProvider == "VoyageAI":
            this.model = VoyageAIEmbeddings(
                model = "voyage-3-lite",
                voyage_api_key = "pa-GKTmAr-t9Nz9-n8rup9GKmMarRxtsWEcB3sROxgVlvT",
                batch_size = 64
            )
        elif embedProvider == "Custom":
            this.model = CustomDenseEmbeddings(
                host = kwargs["custom_host"],
                modelName = embedModel
            )
        elif embedProvider == "None":
            this.model = NoneDenseEmbeddings()
        else:
            raise ValueError(f"Unknown dense embeddings provider {embedProvider}")
        
    def get_running_model(this) -> str:
        return this.modelName
    
    def embed_request(
            this, 
            texts: list[str], 
            isQuery: bool
        ) -> list[list[float]]:
        if not isQuery:
            return this.model.embed_documents(texts)
        elif this.get_running_model().startswith("Custom"):  # Batch processing of queries available
            return this.model.embed_queries(texts)
        else:
            return [this.model.embed_query(t) for t in texts]

    def embed_internal(
            this, 
            texts: list[str], 
            isQuery: bool
        ) -> list[list[float]]:

        cacheObj = this.queryCache if isQuery else this.docCache
        # Check any texts that are already in cache
        result = [None for i in range(len(texts))]
        textsNotInCache = []
        for i in range(len(texts)):
            inCache = cacheObj.get(texts[i])
            if inCache is not None:
                result[i] = inCache.tolist()
            else:
                textsNotInCache.append(texts[i])
                
        # If not all texts were in cache send a request
        if len(textsNotInCache) > 0:

            # Embed documents; to comply with request limits add a one minute timeout 
            try:
                newEmbeds = this.embed_request(textsNotInCache, isQuery)
            except:
                time.sleep(61)
                newEmbeds = this.embed_request(textsNotInCache, isQuery)

            # And put into result and cache
            for i in range(len(result)-1, -1, -1):
                if result[i] is not None:
                    continue
                result[i] = newEmbeds.pop()
                # Use float16 to further save memory
                cacheObj.put(texts[i], np.array(result[i], dtype=np.half))

            # Register used tokens
            add_model_usage(
                this.usageLogName,
                "dense",
                this.get_running_model(),
                sum(get_text_token_len(t) for t in textsNotInCache),
                0,
            )

        return result

    def embed_documents(this, texts: list[str]) -> list[list[float]]:
        return this.embed_internal(texts, False)
    
    def embed_document(this, doc: str) -> list[float]:
        return this.embed_internal([doc], False)[0]
    
    def embed_queries(this, texts: list[str]) -> list[list[float]]:
        return this.embed_internal(texts, True)

    def embed_query(this, query: str) -> list[float]:
        return this.embed_internal([query], True)[0]

class CustomSparseEmbeddings:

    def __init__(this, host : str, modelName : str):
        this.url = host + "/embed_sparse"
        this.modelName = modelName

    def embed_internal(
            this, 
            texts: list[str], 
            isQuery: bool
        ) -> list[dict[str, list[Any]]]:

        return requests.get(
            this.url, 
            json = {
                "data": texts,
                "model": this.modelName,
                "isQuery": isQuery
            }
        ).json()

    def embed_documents(this, texts: list[str]) -> list[dict[str, list[Any]]]:
        return this.embed_internal(texts, False)
    
    def embed_document(this, doc: str) -> dict[str, list[Any]]:
        return this.embed_internal([doc], False)[0]
    
    def embed_queries(this, texts: list[str]) -> list[dict[str, list[Any]]]:
        return this.embed_internal(texts, True)

    def embed_query(this, query: str) -> dict[str, list[Any]]:
        return this.embed_internal([query], True)[0]
    
class NoneSparseEmbeddings:
    """Returns empty sparse embeddings"""
    def __init__(this): pass
    def embed_documents(this, texts: list[str]) -> list[dict[str, list[Any]]]: 
        return [{"indices":[],"values":[]} for t in texts]
    def embed_document(this, doc: str) -> dict[str, list[Any]]:
        return {"indices":[],"values":[]}
    def embed_queries(this, texts: list[str]) -> list[dict[str, list[Any]]]: 
        return [{"indices":[],"values":[]} for t in texts]
    def embed_query(this, query: str) -> dict[str, list[Any]]: 
        return {"indices":[],"values":[]}
    
class SparseEmbeddingsDispatcher:

    def __init__(this, modelName : str, cacheSize : int, **kwargs):
        this.docCache = LRUCache(cacheSize)
        this.queryCache = LRUCache(cacheSize)
        this.modelName = modelName
        this.usageLogName = kwargs.get("usage_log_name", None)

        embedProvider, embedModel = get_provider_and_model(modelName)
        if embedProvider == "Custom":
            this.model = CustomSparseEmbeddings(
                host = kwargs["custom_host"],
                modelName = embedModel
            )
        elif embedProvider == "None":
            this.model = NoneSparseEmbeddings()
        else:
            raise ValueError(f"Unknown sparse embeddings provider {embedProvider}")
        
    def get_running_model(this) -> str:
        return this.modelName

    def embed_internal(
            this, 
            texts: list[str], 
            isQuery: bool
        ) -> list[dict[str, list[Any]]]:

        cacheObj = this.queryCache if isQuery else this.docCache
        # Check any texts that are already in cache
        result = [None for i in range(len(texts))]
        textsNotInCache = []
        for i in range(len(texts)):
            inCache = cacheObj.get(texts[i])
            if inCache is not None:
                result[i] = {
                    "indices": inCache[0].tolist(),
                    "values": inCache[1].tolist()
                }
            else:
                textsNotInCache.append(texts[i])

        # If not all texts were in cache send a request
        if len(textsNotInCache) > 0:
            if not isQuery:
                newEmbeds = this.model.embed_documents(textsNotInCache)
            elif this.get_running_model().startswith("Custom"):  # Batch processing of queries available
                newEmbeds = this.model.embed_queries(textsNotInCache)
            else:
                newEmbeds = [this.model.embed_query(t) for t in textsNotInCache]

            # And put into result and cache
            for i in range(len(result)-1, -1, -1):
                if result[i] is not None:
                    continue
                result[i] = newEmbeds.pop()
                # Use float16 to further save memory
                cacheObj.put(
                    texts[i],
                    (
                        np.array(result[i]["indices"], dtype=np.int32),
                        np.array(result[i]["values"], dtype=np.half)
                    )
                )

            # Register used tokens
            add_model_usage(
                this.usageLogName,
                "sparse",
                this.get_running_model(),
                sum(get_text_token_len(t) for t in textsNotInCache),
                0,
            )

        return result

    def embed_documents(this, texts: list[str]) -> list[dict[str, list[Any]]]:
        return this.embed_internal(texts, False)
    
    def embed_document(this, doc: str) -> dict[str, list[Any]]:
        return this.embed_internal([doc], False)[0]
    
    def embed_queries(this, texts: list[str]) -> list[dict[str, list[Any]]]:
        return this.embed_internal(texts, True)

    def embed_query(this, query: str) -> dict[str, list[Any]]:
        return this.embed_internal([query], True)[0]
    
class CustomReranker:

    def __init__(this, host : str, modelName : str):
        this.url = host + "/rerank"
        this.modelName = modelName

    def rerank(this, documents : list[str], query : str) -> list[dict[str, Any]]:
        scores = requests.get(
            this.url, 
            json = {
                "data": [query] + documents,
                "model": this.modelName
            }
        ).json()
        sortedIndexes = [i[0] for i in sorted(enumerate(scores), key=lambda x:x[1], reverse=True)]
        return [{"index":index, "relevance_score":scores[index]} for index in sortedIndexes]
    
class TogetherReranker:

    URL = "https://api.together.xyz/v1/rerank"

    def __init__(this, apiKey : str, modelName : str):
        this.apiKey = apiKey
        this.modelName = modelName

    def rerank(this, documents : list[str], query : str) -> list[dict[str, Any]]:
        payload = {
            "model": this.modelName,
            "query": query,
            "return_documents": False,
            "documents": documents,
            "top_n": len(documents)  #Return scores of everything
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " + this.apiKey
        }
        response = requests.post(this.URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["results"]
    
class RerankerDispatcher:

    def __init__(this, modelName : str, cacheSize : int, **kwargs):
        this.cache = LRUCache(cacheSize)
        this.modelName = modelName
        this.usageLogName = kwargs.get("usage_log_name", None)

        rerankProvider, rerankModel = get_provider_and_model(modelName)
        if rerankProvider == "Custom":
            this.reranker = CustomReranker(
                host = kwargs["custom_host"],
                modelName = rerankModel
            )
        elif rerankProvider == "Jina":
            this.reranker = JinaRerank(
                jina_api_key = kwargs["jina_api_key"],
                model = rerankModel,
                top_n = None
            )
        elif rerankProvider == "Together":
            this.reranker = TogetherReranker(
                apiKey = kwargs["together_api_key"],
                modelName = rerankModel
            )
        elif rerankProvider == "VoyageAI":
            this.reranker = VoyageAIRerank(
                voyageai_api_key = kwargs["voyageai_api_key"],
                model = rerankModel,
                top_k = None
            )
        else:
            raise ValueError(f"Unknown reranker provider {rerankProvider}")
        
    def get_running_model(this) -> str:
        return this.modelName

    def rerank(this, documents : list[str], query : str) -> list[dict[str, Any]]:

        # Check any query:doc pair already in cache
        scores : list[float] = [None for i in range(len(documents))]
        textsNotInCache : list[int] = []  # Stores indices
        for i in range(len(documents)):
            inCache = this.cache.get((query, documents[i]))
            if inCache is not None:
                scores[i] = inCache
            else:
                textsNotInCache.append(i)

        # Rerank any missing score
        if len(textsNotInCache) > 0:
            result = this.reranker.rerank([documents[idx] for idx in textsNotInCache], query)
            for element in result:
                index = textsNotInCache[element["index"]]
                this.cache.put((query, documents[index]), element["relevance_score"])
                scores[index] = element["relevance_score"]

        add_model_usage(
            this.usageLogName,
            "reranker",
            this.get_running_model(),
            sum(get_text_token_len(t) + get_text_token_len(query) for t in documents),
            0,
        )
        sortedIndexes = [i[0] for i in sorted(enumerate(scores), key=lambda x:x[1], reverse=True)]
        return [{"index":index, "relevance_score":scores[index]} for index in sortedIndexes]
    
class CustomTranscriber:

    def __init__(this, host : str, model : str):
        this.url = host + "/transcribe"
        this.model = model

    def invoke(this, audioSamples : list[float]) -> dict[str, list[Any]]:
        return requests.get(
            this.url, 
            json = {
                "samples": audioSamples,
                "model": this.model
            }
        ).json()
    
class TranscriberDispatcher:

    def __init__(this, modelName : str, **kwargs):
        this.modelName = modelName
        this.usageLogName = kwargs.get("usage_log_name", None)

        trancriberProvider, trancriberModel = get_provider_and_model(modelName)
        if trancriberProvider == "Custom":
            this.transcriber = CustomTranscriber(
                host = kwargs["custom_host"],
                model = trancriberModel
            )
        else:
            raise ValueError(f"Unknown transcriber provider {trancriberProvider}")
        
    def get_running_model(this) -> str:
        return this.modelName
        
    def invoke(this, audioSamples : list[float]) -> dict[str, list[Any]]:
        """
        Transcribes with the given audio samples.

        Args:
            audioSamples: audio to transcribe. Must be in 16KHz
        Returns: 
            a dictionary with the keys "text" and "timestamp". Both contain 
            lists. For "text" the list contains sentences, and for "timestamp" 
            it contains the second where that sentence starts. 
        """
        add_model_usage(
            this.usageLogName,
            "transcriber",
            this.get_running_model(),
            len(audioSamples) // 16000,
            0,
        )
        return this.transcriber.invoke(audioSamples)
    
class LLMDispatcher:

    def __init__(this, modelName : str, max_context : int = 2048, temperature : float = 0.6, **kwargs):
        this.modelName = modelName
        this.usageLogName = kwargs.get("usage_log_name", None)

        llmProvider, llmModel = get_provider_and_model(modelName)
        if llmProvider == "Ollama":
            this.llm = ChatOllama(
                base_url = kwargs["ollama_host"], 
                model = llmModel, 
                temperature = temperature,
                num_ctx = max_context
            )
        elif llmProvider == "Google":
            this.llm = ChatGoogleGenerativeAI(
                model = llmModel,
                temperature = temperature,
                google_api_key = kwargs["google_api_key"],
                max_tokens = None,
                timeout = None,
                max_retries = 5
            )
        elif llmProvider == "OpenAI":
            this.llm = ChatOpenAI(
                model = llmModel,
                temperature = temperature,
                openai_api_key = kwargs["openai_api_key"],
                max_tokens = None,
                timeout = None,
                max_retries = 2,
            )
        elif llmProvider == "Together":
            this.llm = ChatTogether(
                model = llmModel,
                temperature = temperature,
                api_key = kwargs["together_api_key"],
                max_tokens = None,
                timeout = None,
                max_retries = 5,
            )
        else:
            raise ValueError(f"Unknown llm provider {llmProvider}")
        
    def get_running_model(this) -> str:
        return this.modelName
    
    def add_usage(this, text : str, type : str):
        tokens = get_text_token_len(text)
        add_model_usage(
            this.usageLogName,
            "llm",
            this.get_running_model(),
            tokens if type == "in" else 0,
            tokens if type == "out" else 0,
        )
        
    def invoke(this, input : Any) -> str:
        result = this.llm.invoke(input)
        if this.usageLogName is not None:
            this.add_usage(input if type(input) is str else input.to_string(), "in")
            this.add_usage(result.content, "out")
        return result.content
    
    def stream(this, input : Any) -> Any:
        if this.usageLogName is not None:
            this.add_usage(input if type(input) is str else input.to_string(), "in")
        r = this.llm.invoke(input)
        print(r.usage_metadata)
        return this.llm.stream(input)

    def end_stream(this, input : str):
        """Calling this function is not obligatory, it is simply to record the generated tokens"""
        if this.usageLogName is not None:
            this.add_usage(input, "out")
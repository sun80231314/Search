#coding=utf-8
import redis
from django.shortcuts import render
from django.views.generic.base import View
from elasticsearch import Elasticsearch
from datetime import datetime

client = Elasticsearch(hosts=["localhost"])

class SearchView(View):
    @staticmethod
    def get(request):
        key_words = request.GET.get("q", "")
        print(key_words)
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()
        response = client.search(
            index="jobbole111",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["title", "content"]
                    }
                },
                "from": (page - 1) * 10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ["</span>"],
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "highlight" in hit and "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = "".join(hit["_source"]["title"])
            if "highlight" in hit and "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]+"</span>"
            else:
                hit_dict["content"] = "".join(hit["_source"]["content"])[:500]+"</span>"

            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]
            hit_list.append(hit_dict)
        return render(request, "result.html", {"page": page,
                                               "total_nums": total_nums,
                                               "all_this": hit_list,
                                               "key_words": key_words,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds})

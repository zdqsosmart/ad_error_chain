import json
import os
from typing import TypedDict, List, Literal

import pandas as pd
from langchain.agents import AgentState
from langchain_openai import ChatOpenAI

from src.utils.db_manager import PostgreManager
from src.utils.mylog import getMyLog

logger = getMyLog()
def init_data():
    """加载将于处理的广告创建异常"""
    try:
        with PostgreManager() as db:
            res = db.fetch_all_then_return_dataframe(
                "select distinct entity,note from business.amazon_advertising_auto_table")
            data = []


            for idx,row in res.iterrows():
                item = {"entity": row["entity"]}
                notes = json.loads(row["note"].replace("'",'"'))
                for note in notes:
                    item_ = item.copy()
                    item_["rangeError_message"] = note.get("rangeError",{}).get("message","")
                    item_["otherError_message"] = note.get("otherError", {}).get("message","")
                    item_["adEligibilityError_message"] = note.get("adEligibilityError", {}).get("message","")
                    item_["entityStateError_message"] = note.get("entityStateError", {}).get("message","")

                    item_["rangeError_reason"] = note.get("rangeError", {}).get("reason","")
                    item_["otherError_reason"] = note.get("otherError", {}).get("reason","")
                    item_["adEligibilityError_reason"] = note.get("adEligibilityError", {}).get("reason","")
                    item_["entityStateError_reason"] = note.get("entityStateError", {}).get("reason","")
                    data.append(item_)
            return data

    except Exception as e:
        logger.error(note)
        logger.error(e)

def init_llm():
    model_set = {}
    # GPT
    gpt_mini_llm = ChatOpenAI(model="gpt-4.1-mini"
                         ,api_key=os.getenv("XIAOAI_API_KEY")
                         ,base_url=os.getenv("XIAOAI_BASE_URL"))
    model_set["GPT_MINI"] = gpt_mini_llm

    # deepseek
    deepseek_llm = ChatOpenAI(model="deepseek-chat"
                         , api_key=os.getenv("DEEPSEEK_API_KEY")
                         , base_url=os.getenv("DEEPSEEK_BASE_URL"))
    model_set["DEEPSEEK"] = deepseek_llm

    # qwen
    qwen_llm = ChatOpenAI(model="qwen-max"
                              , api_key=os.getenv("BAILIAN_API_KEY")
                              , base_url=os.getenv("BAILIAN_BASE_URL"))
    model_set["QWEN"] = qwen_llm
    return model_set


class ErrorStatic(TypedDict):
    # storeid:str
    entity:str
    message:str
    reason:str
    error_happend_num:int

class ErrorAgentState(AgentState):

    # 错误信息统计
    error_info:ErrorStatic

    # 处理人员分类
    classification:Literal["运营人员", "开发人员"]

    # 问题处理人员
    person_todo:str | None

    # 问题解析与处理方法参考
    explanation:str | None
    solution:str | None

    # 回复内容
    draft_response: str | None

# --------------- Tool Start --------------------
def read_error_message(batch=10) -> list:
    pass


# --------------- Tool End --------------------

def build_agent():
    pass





if __name__ == '__main__':
    init_data()
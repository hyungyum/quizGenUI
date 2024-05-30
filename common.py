# common.py

import os
import json
import pandas as pd
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field

def load_llm(api_key: str, use_gpt4: bool = False) -> ChatOpenAI:
    model = "gpt-4o" if use_gpt4 else "gpt-3.5-turbo"
    return ChatOpenAI(model=model, api_key=api_key)

def initialize_session_state(session_state, index):
    keys = ["context", "quiz_generated", "quiz_data", "user_answers", "show_results"]
    for key in keys:
        if f"{key}{index}" not in session_state:
            session_state[f"{key}{index}"] = None if key == "context" else False if key == "quiz_generated" else []

def create_gift_format(quiz_data, context):
    gift_data = "// question: 0  name: Switch category to $course$/인문·사회에서의 AI활용 의 기본설정/인공신경망 구조 및 학습\n"
    gift_data += "$CATEGORY: $course$/인문·사회에서의 AI활용 의 기본설정/인공신경망 구조 및 학습\n\n"
    for i, question in enumerate(quiz_data.questions):
        question_number = 540535 + i
        gift_data += f"// question: {question_number}  name: {context}\n"
        gift_data += f"::{context}::[html]<p>{question}</p>{{\n"
        for alt in quiz_data.alternatives[i]:
            if alt == quiz_data.answers[i]:
                gift_data += f"=<p>{alt}</p>\n"
            else:
                gift_data += f"~<p>{alt}</p>\n"
        gift_data += "}\n\n"
    return gift_data

def create_xhtml_format(quiz_data):
    xhtml_data = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<title>Moodle Quiz XHTML Export</title>
<style type="text/css">
body {
     font-family: verdana, helvetica, sans-serif;
     background-color: #fff;
     color: #000;
 }
 .question {
     border: 1px solid #ddd;
     margin: 5px;
     padding: 3px;
 }
 .question h3 {
     font-weight: normal;
     font-size: 125%;
 }
 .question ul {
     list-style-type: none;
 }
</style>
</head>
<body>
<form action="...REPLACE ME..." method="post">\n\n"""
    for i, question in enumerate(quiz_data.questions):
        xhtml_data += f"""<!-- question: {i} -->
<div class="question">
<h3>Q{i+1}</h3>
<p class="questiontext">{question}</p>
<ul class="multichoice">\n"""
        for alt in quiz_data.alternatives[i]:
            xhtml_data += f"""  <li><input name="quest_{i}" type="radio" value="{alt}" /><p>{alt}</p></li>\n"""
        xhtml_data += "</ul>\n</div>\n\n"
    xhtml_data += """<p class="submit">
  <input type="submit" />
</p>
</form>
</body>
</html>"""
    return xhtml_data

def create_xml_format(quiz_data):
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<quiz>\n"""
    for i, question in enumerate(quiz_data.questions):
        xml_data += f"""  <question type="multichoice">
    <name>
      <text>Q{i+1}</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[{question}]]></text>
    </questiontext>
    <answer fraction="100" format="html">
      <text><![CDATA[{quiz_data.answers[i]}]]></text>
    </answer>\n"""
        for alt in quiz_data.alternatives[i]:
            if alt != quiz_data.answers[i]:
                xml_data += f"""    <answer fraction="0" format="html">
      <text><![CDATA[{alt}]]></text>
    </answer>\n"""
        xml_data += "  </question>\n\n"
    xml_data += "</quiz>"
    return xml_data

def export_quiz_data(quiz_data, context, export_format):
    quiz_data_json = json.dumps(quiz_data.dict(), ensure_ascii=False)
    if export_format == "JSON":
        return quiz_data_json, "application/json", "quiz_data.json"
    elif export_format == "CSV":
        quiz_df = pd.DataFrame({
            "question": quiz_data.questions,
            "answer": quiz_data.answers,
            "alternatives": [', '.join(alt) for alt in quiz_data.alternatives]
        })
        csv_data = quiz_df.to_csv(index=False)
        return csv_data, "text/csv", "quiz_data.csv"
    elif export_format == "TXT":
        txt_data = ""
        for i, question in enumerate(quiz_data.questions):
            txt_data += f"Q{i+1}: {question}\n"
            for alt in quiz_data.alternatives[i]:
                txt_data += f"- {alt}\n"
            txt_data += f"Answer: {quiz_data.answers[i]}\n\n"
        return txt_data, "text/plain", "quiz_data.txt"
    elif export_format == "GIFT":
        gift_data = create_gift_format(quiz_data, context)
        return gift_data, "text/plain", "quiz_data.txt"
    elif export_format == "XHTML":
        xhtml_data = create_xhtml_format(quiz_data)
        return xhtml_data, "text/html", "quiz_data.html"
    elif export_format == "XML":
        xml_data = create_xml_format(quiz_data)
        return xml_data, "application/xml", "quiz_data.xml"
    return None, None, None


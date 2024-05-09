import streamlit as st
import os
# from dotenv import load_dotenv
# load_dotenv()

from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field

class QuizMultipleChoice(BaseModel):
    quiz_text: str = Field(description="The quiz test")
    questions: List[str] = Field(description="The quiz quesitons")
    alternatives: List[List[str]] = Field(description="The quiz alternatives")
    answers: List[str] = Field(description="The quiz answers")

class QuizTrueFalse(BaseModel):
    quiz_text: str = Field(description="The quiz test")
    questions: List[str] = Field(description="The quiz quesitons")
    alternatives: List[List[str]] = Field(description="The quiz alternatives")
    answers: List[str] = Field(description="The quiz answers")

class QuizOpenEnded(BaseModel):
    questions: List[str] = Field(description="The quiz quesitons")
    answers: List[str] = Field(description="The quiz answers")

def create_quiz_chain(prompt_template, llm, pydantic_object_schema):
    """Creates the chain for the quiz app."""
    return prompt_template | llm.with_structured_output(pydantic_object_schema)

def create_multiple_choice_template():
    """Create the prompt template for the quiz app."""
    
    template = """ 
    You are an expert quiz maker for technical fields. Let's think step by step and
    create a quiz with {num_questions} questions about the following concept/content: {quiz_context}.

    The format of the quiz could be one of the following:
    
    - Multiple-choice: 
    - Questions:
        <Question1>: 
            - Alternatives1: <option 1>, <option 2>, <option 3>, <option 4>
        <Question2>: 
            - Alternatives2: <option 1>, <option 2>, <option 3>, <option 4>
        ....
        <QuestionN>: 
            - AlternativesN: <option 1>, <option 2>, <option 3>, <option 4>
    - Answers:
        <Answer1>: <option 1 | option 2 | option 3 | option 4>
        <Answer2>: <option 1 | option 2 | option 3 | option 4>
        ....
        <AnswerN>: <option 1 | option 2 | option 3 | option 4>
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def create_true_false_template():
    """Create the prompt template for the quiz app."""
    
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and
    create a quiz with {num_questions} questions about the following concept/content: {quiz_context}.

    The format of the quiz could be one of the following:
    - True-false:

    - Questions:
        <Question1>: 
            - Alternatives1: <True>, <False>
        <Question2>: 
            - Alternatives2: <True>, <False>
        .....
        <QuestionN>: 
            - AlternativesN: <True>, <False>
    - Answers:
        <Answer1>: <True|False>
        <Answer2>: <True|False>
        .....
        <AnswerN>: <True|False>
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def create_open_ended_template():
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and
    create a quiz with {num_questions} questions about the following concept/content: {quiz_context}.

    The format of the quiz could be one of the following:
    - Open-ended:
    - Questions:
        <Question1>: 
        <Question2>:
        .....
        <QuestionN>:
    - Answers:    
        <Answer1>:
        <Answer2>:
        .....
        <AnswerN>:
       
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def main():
    st.title("Quiz App")
    st.write("This app generates a quiz based on a given context.")
    llm = ChatOpenAI()
    context = st.text_area("Enter the concept/context for the quiz")
    num_questions = st.number_input("Enter the number of questions", min_value=1, max_value=10, value=3)
    quiz_type = st.selectbox("Select the quiz type", ["multiple-choice", "true-false", "open-ended"])

    # 퀴즈 유형 변경 시 상태 초기화
    if 'quiz_type' not in st.session_state or st.session_state.quiz_type != quiz_type:
        st.session_state.quiz_type = quiz_type
        st.session_state.quiz_data = None
        st.session_state.user_answers = None

    if st.button("Generate Quiz"):
        if quiz_type == "multiple-choice":
            prompt_template = create_multiple_choice_template()
            pydantic_object_schema = QuizMultipleChoice
        elif quiz_type == "true-false":
            prompt_template = create_true_false_template()
            pydantic_object_schema = QuizTrueFalse
        else:
            prompt_template = create_open_ended_template()
            pydantic_object_schema = QuizOpenEnded

        chain = create_quiz_chain(prompt_template, llm, pydantic_object_schema)
        st.session_state.quiz_data = chain.invoke({"num_questions": num_questions, "quiz_context": context})
        st.session_state.user_answers = [None] * len(st.session_state.quiz_data.questions) if st.session_state.quiz_data else []


    if 'quiz_data' in st.session_state and st.session_state.quiz_data:
        user_answers = {}
        for idx, question in enumerate(st.session_state.quiz_data.questions):
            st.write(f"**{idx + 1}. {question}**")
            if quiz_type != "open-ended":
                options = st.session_state.quiz_data.alternatives[idx]
                # 선택지에 라벨을 추가하지 않고, 직접 사용합니다.
                formatted_options = {option: option for option in options}
                user_answer_key = st.radio("Select an answer:", list(formatted_options.keys()), key=idx)
                user_answers[idx] = user_answer_key  # 직접 'True' 또는 'False'를 저장합니다.
            else:
                user_answers[idx] = st.text_area("Your answer:", key=idx)
        if st.button("Score Quiz"):
            score = 0
            correct_answers = []
            for idx, question in enumerate(st.session_state.quiz_data.questions):
                correct_answer = st.session_state.quiz_data.answers[idx]
                if quiz_type != "open-ended":
                    if user_answers[idx] == correct_answer:
                        score += 1
                correct_answers.append(f"{idx + 1}. {correct_answer}")
            st.write("Quiz results:")
            st.write(f"Your score: {score}/{len(st.session_state.quiz_data.questions)}")
            for correct_answer in correct_answers:
                st.write(correct_answer)


if __name__ == "__main__":
    main()


from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from typing import List

class QuizMultipleChoice(BaseModel):
    questions: List[str] = Field(description="The quiz questions")
    alternatives: List[List[str]] = Field(description="The quiz alternatives")
    answers: List[str] = Field(description="The quiz answers")

class QuizTrueFalse(BaseModel):
    questions: List[str] = Field(description="The quiz questions")
    alternatives: List[List[str]] = Field(description="The quiz alternatives")
    answers: List[str] = Field(description="The quiz answers")

class QuizOpenEnded(BaseModel):
    questions: List[str] = Field(description="The quiz questions")
    answers: List[str] = Field(description="The quiz answers")

class QuizShortAnswer(BaseModel):
    questions: List[str] = Field(description="The quiz questions")
    answers: List[str] = Field(description="The quiz answers")


def create_quiz_chain(prompt_template, llm, pydantic_object_schema):
    """Creates the chain for the quiz app."""
    return prompt_template | llm.with_structured_output(pydantic_object_schema)


def create_multiple_choice_template(language, user_input=None):
    # """Create the prompt template for the quiz app, including conditional translation."""
    
    # template = """ 
    # You are an expert quiz maker for technical fields. Let's think step by step and create a multiple-choice quiz in English with {num_questions} questions about the following concept/content: {quiz_context}.
    # Ensure that the quiz is suitable for an audience with {difficulty} level knowledge.

    # The format of the quiz should be as follows:
    # - Questions:
    #     <Question1>: 
    #         - Alternatives1: <option 1>, <option 2>, <option 3>, <option 4>
    #     <Question2>: 
    #         - Alternatives2: <option 1>, <option 2>, <option 3>, <option 4>
    #     .....
    #     <QuestionN>: 
    #         - AlternativesN: <option 1>, <option 2>, <option 3>, <option 4>
    # - Answers:
    #     <Answer1>: <option 1 | option 2 | option 3 | option 4>
    #     <Answer2>: <option 1 | option 2 | option 3 | option 4>
    #     .....
    #     <AnswerN>: <option 1 | option 2 | option 3 | option 4>
    # """

    """Create the prompt template for the quiz app, including conditional translation."""
    template = """ 
    You are an expert quiz maker for technical fields. Let's think step by step and
    create a {difficulty} quiz with {num_questions} multiple-choice questions about the following concept/content: {quiz_context}.

    The format of the quiz should be as follows:

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

    if language != 'English':
        # template += f"""
        # \nPlease note: After generating the quiz in English according to the above conditions, translate the entire quiz questions (including alternatives) and answers that you just have generated above into the clicked {language}. Ensure that: 
        # - Code snippets, technical terms, and specific names are not translated.
        # - The translated quiz maintains the technical accuracy and clarity of the original English version.
        # """
        template += f"\n\nPlease ensure that the quiz is accurately translated into {language}, maintaining the technical accuracy and clarity of the questions and options."


    if user_input:
        template += f"\n\nAdditional instructions: {user_input}"

    prompt = ChatPromptTemplate.from_template(template)
    return prompt


def create_true_false_template(language, user_input=None):
    """Create the prompt template for the quiz app."""
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and create a true/false quiz in English with {num_questions} questions about the following concept/content: {quiz_context}.

    Ensure that the quiz is suitable for an audience with {difficulty} level knowledge.

    The format of the quiz should be as follows:
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

    if language != 'English':
        # template += f"""
        # After creating the quiz in English, Please translate all the questions, alternatives, and answers into {language}. 
        # Ensure that code snippets, technical terms, and specific names are not translated. 
        # The translated quiz should maintain the technical accuracy and clarity of the original English version.
        # """
        template += f"\n\nPlease ensure that the quiz is accurately translated into {language}, maintaining the technical accuracy and clarity of the questions and options."

    if user_input:
        template += f"\n\nAdditional instructions: {user_input}"

    prompt = ChatPromptTemplate.from_template(template)
    return prompt


def create_open_ended_template(language, user_input=None):
    """Create the prompt template for the quiz app."""
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and create an open-ended quiz in English with {num_questions} questions about the following concept/content: {quiz_context}.

    Ensure that the quiz is suitable for an audience with {difficulty} level knowledge.

    The format of the quiz should be as follows:
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

    if language != 'English':
        # template += f"""
        # After creating the quiz in English, Please translate all the questions and answers into {language}. 
        # Ensure that code snippets, technical terms, and specific names are not translated. 
        # The translated quiz should maintain the technical accuracy and clarity of the original English version.
        # """
        template += f"\n\nPlease ensure that the quiz is accurately translated into {language}, maintaining the technical accuracy and clarity of the questions and options."

    if user_input:
        template += f"\n\nAdditional instructions: {user_input}"

    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def create_short_answer_template(language, user_input=None):
    """Create the prompt template for the quiz app."""
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and create a short-answer quiz in English with {num_questions} questions about the following concept/content: {quiz_context}.
    Ensure that the quiz is suitable for an audience with {difficulty} level knowledge.

    The format of the quiz should be as follows:
    - Questions:
        <Question1>: 
        <Question2>:
        .....
        <QuestionN>:
    - Answers:
        Provide a brief answer in one or two words for each question. The answer should be concise and to the point.
        <Answer1>:
        <Answer2>:
        .....
        <AnswerN>:
    """

    if language != 'English':
        # template += f"""
        # After creating the quiz in English, Please translate all the questions and answers into {language}. 
        # Ensure that code snippets, technical terms, and specific names are not translated. 
        # The translated quiz should maintain the technical accuracy and clarity of the original English version.
        # """
        template += f"\n\nPlease ensure that the quiz is accurately translated into {language}, maintaining the technical accuracy and clarity of the questions and options."

    if user_input:
        template += f"\n\nAdditional instructions: {user_input}"

    prompt = ChatPromptTemplate.from_template(template)
    return prompt

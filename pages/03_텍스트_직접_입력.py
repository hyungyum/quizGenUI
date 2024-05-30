import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append('../')
from common import (
    load_llm,
    initialize_session_state,
    export_quiz_data,
    create_gift_format,
    create_xhtml_format,
    create_xml_format
)
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from promptTemplates import QuizMultipleChoice, QuizTrueFalse, QuizOpenEnded, QuizShortAnswer, create_quiz_chain, create_multiple_choice_template, create_true_false_template, create_open_ended_template, create_short_answer_template
from htmlTemplates import css, footer_css, footer_html

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def select_chunk_set(vectorstore, text_chunks, num_vectors=5):
    chunks = text_chunks[:5]
    context = ' '.join(chunks)
    return context

def main():
    st.set_page_config(page_title="Text 기반 문제 생성", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    st.header("QuizGen :books:")
    st.caption("Text(긴 글) 업로드 후 원하시는 문제를 선택하여 주십시오.")

    api_key = os.getenv("OPENAI_API_KEY")
    use_gpt4 = st.toggle("GPT-4")
    llm = load_llm(api_key, use_gpt4)

    raw_text = st.text_area("텍스트(긴 글) 입력란", height=150)

    initialize_session_state(st.session_state, 3)

    if st.button("입력"):
        with st.spinner("입력 중"):
            text_chunks = get_text_chunks(raw_text)
            vectorstore = get_vectorstore(text_chunks)
            st.session_state.context3 = select_chunk_set(vectorstore, text_chunks)
            st.success('저장 완료!', icon="✅")

    col1, col2, col3 = st.columns(3)

    with col3:
        difficulty = st.radio("난이도", ["easy", "normal", "hard"], index=1)

    with col1:
        language = st.radio("언어 선택", ["Korean", "English"], index=0)

    with col2:
        quiz_type = st.radio("종류 선택", ["객관식", "참/거짓", "주관식", "단답형"], index=0)

    num_questions = st.number_input("갯수 선택", min_value=1, max_value=10, value=3)
    user_input = st.text_area("기타 요구 사항을 입력해 주십시오.")

    if st.button("문제 생성"):
        if st.session_state.context3:
            if quiz_type == "객관식":
                prompt_template = create_multiple_choice_template(language, user_input)
                pydantic_object_schema = QuizMultipleChoice
            elif quiz_type == "참/거짓":
                prompt_template = create_true_false_template(language, user_input)
                pydantic_object_schema = QuizTrueFalse
            elif quiz_type == "단답형":
                prompt_template = create_short_answer_template(language, user_input)
                pydantic_object_schema = QuizShortAnswer
            else:
                prompt_template = create_open_ended_template(language, user_input)
                pydantic_object_schema = QuizOpenEnded

            st.write("(생성 중) 에러 발생시, 생성 버튼을 다시 눌러 주십시오.")
            chain = create_quiz_chain(prompt_template, llm, pydantic_object_schema)
            st.session_state.quiz_data3 = chain.invoke(
                {"num_questions": num_questions, "quiz_context": st.session_state.context3, "difficulty": difficulty})
            st.session_state.user_answers3 = [None] * len(
                st.session_state.quiz_data3.questions) if st.session_state.quiz_data3 else []
            st.session_state.quiz_generated3 = True
            st.session_state.show_results3 = False
        else:
            st.write("텍스트를 입력란에 입력해 주십시오.")

    if st.session_state.quiz_generated3 and st.session_state.quiz_data3:
        for idx, question in enumerate(st.session_state.quiz_data3.questions):
            st.write(f"**{idx + 1}. {question}**")
            if quiz_type == "객관식" or quiz_type == "참/거짓":
                options = st.session_state.quiz_data3.alternatives[idx]
                st.session_state.user_answers3[idx] = st.radio("답:", options, key=f"user_answer3_{idx}", index=None)
                if st.session_state.show_results3:
                    correct_answer = st.session_state.quiz_data3.answers[idx]
                    if st.session_state.user_answers3[idx] == correct_answer:
                        st.success(f"정답: {correct_answer}")
                    else:
                        st.error(f"정답: {correct_answer}")
            elif quiz_type == "단답형":
                st.session_state.user_answers3[idx] = st.text_input("답:", key=f"user_answer3_{idx}")
                if st.session_state.show_results3:
                    correct_answer = st.session_state.quiz_data3.answers[idx]
                    if st.session_state.user_answers3[idx].strip() == correct_answer.strip():
                        st.success(f"정답: {correct_answer}")
                    else:
                        st.error(f"정답: {correct_answer}")
            else:
                st.session_state.user_answers3[idx] = st.text_area("답:", key=f"user_answer3_{idx}")
                if st.session_state.show_results3:
                    correct_answer = st.session_state.quiz_data3.answers[idx]
                    if st.session_state.user_answers3[idx].strip() == correct_answer.strip():
                        st.success(f"정답: {correct_answer}")
                    else:
                        st.error(f"정답: {correct_answer}")

        if st.button("채점"):
            score = 0
            correct_answers = []
            for idx, question in enumerate(st.session_state.quiz_data3.questions):
                correct_answer = st.session_state.quiz_data3.answers[idx]
                if quiz_type != "주관식":
                    if st.session_state.user_answers3[idx] == correct_answer:
                        score += 1
                correct_answers.append(f"{idx + 1}. {correct_answer}")

            st.session_state.show_results3 = True
            st.session_state.score3 = score
            st.session_state.correct_answers3 = correct_answers
            st.rerun()

    if st.session_state.show_results3:
        st.subheader("채점 결과")
        st.write(f"점수: {st.session_state.score3}/{len(st.session_state.quiz_data3.questions)}")
        expander = st.expander("정답 보기")
        for correct_answer in st.session_state.correct_answers3:
            expander.write(correct_answer)

    if st.session_state.quiz_data3:
        export_format = st.selectbox("내보낼 형식을 선택하세요", ["JSON", "CSV", "TXT", "GIFT", "XHTML", "XML"])
        data, mime, filename = export_quiz_data(st.session_state.quiz_data3, st.session_state.context3, export_format)
        if data and mime and filename:
            st.download_button(label=f"퀴즈 다운로드 ({export_format})", data=data, file_name=filename, mime=mime)

    st.markdown(footer_css, unsafe_allow_html=True)
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

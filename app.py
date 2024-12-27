import json
import ollama
import re
import streamlit as st
import wikipediaapi


EN_LOCALE = 'en' 
ZH_LOCALE = 'zh' 

with open("./user_agent.cfg", "r") as f:
    email = json.load(f)["email"]
USER_AGENT = f"Wikipedia-API ZH/EN ({email})"
WIKI_ZH = wikipediaapi.Wikipedia(USER_AGENT, ZH_LOCALE)
WIKI_EN = wikipediaapi.Wikipedia(USER_AGENT, EN_LOCALE)

LEVEL_STRING = {
    "traditional": {
        "elementary": "小學生",
        "middle": "國中生",
        "high": "高中生",
    },
    "simplified": {
        "elementary": "小学生",
        "middle": "初中生",
        "high": "高中生"
    }
}

@st.cache_data(persist="disk")
def get_page(lang, term):
    if lang == EN_LOCALE:
        return WIKI_EN.page(term)
    elif lang == ZH_LOCALE:
        return WIKI_ZH.page(term)

def simplify_text(instruction, input_text, level, script_type):
    inst = instruction.format(LEVEL_STRING[script_type][level], input_text)
    prompt = f"{inst}\n\n{input_text.strip()}"
    print("Final prompt:\n", prompt)
    stream = ollama.generate(model='glm4', prompt=prompt, stream=True)
    for chunk in stream:
        yield chunk["response"]

def init_blank_keys(str_keys=[], bool_keys=[]):
    for key in str_keys:
        if key not in st.session_state:
            st.session_state[key] = ""
    for key in bool_keys:
        if key not in st.session_state:
            st.session_state[key] = False

def contains_chinese(text):
    zh_pattern = r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]'
    return bool(re.search(zh_pattern, text))

def display_text(search_term):
    page_en = get_page(EN_LOCALE, search_term)
    if page_en.exists():
        # Check if there is a corresponding page in Traditional Chinese
        lang_links = page_en.langlinks
        if ZH_LOCALE in lang_links:
            page_zh = get_page(ZH_LOCALE, lang_links[ZH_LOCALE].title)
            st.session_state.en_title = page_en.title
            st.session_state.zh_title = page_zh.title
            st.session_state.en_preview = page_en.summary[:500] + "..."
            st.session_state.zh_preview = page_zh.summary[:200] + "..."
            st.session_state.wiki_success = True
        else:
            st.session_state.wiki_success = False
            st.error("The page does not have a corresponding Chinese version on Wikipedia.")
    else:
        st.session_state.wiki_success = False
        st.error("The page does not exist on English Wikipedia.")
    st.session_state.wiki_summary = page_zh.summary

st.set_page_config(page_title="Simplify Chinese")
st.title("Chinese Simplifying Tool")
init_blank_keys(str_keys=["en_title", "zh_title", "en_preview", "zh_preview"], bool_keys=["wiki_success"])

st.header("Search from Wikipedia")
search_term = st.text_input("Enter a term to search (can be in English):")
page = None

st.button("Search", on_click=display_text, args=[search_term])

if st.session_state.wiki_success:
    st.subheader(f"Page Title: {st.session_state.zh_title} ({st.session_state.en_title})")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**English Preview:**")
        st.write(st.session_state.en_preview) 
    with col2:
        st.write("**Chinese Preview:**")
        st.write(st.session_state.zh_preview)
    st.caption("Note: Only pulling article summaries for length reasons.")
st.divider()

input_text = st.text_area("Or, enter your own text here:")
st.caption("Note: Typed text will take priority.")
st.divider()

SELECTBOX_MAP = {
    "elementary": "Elementary (小学/小學)",
    "middle": "Middle School (初中/國中)",
    "high": "High School (高中)",
}

level = st.selectbox(
    "Level:",
    list(LEVEL_STRING["simplified"].keys()),
    format_func=lambda x: SELECTBOX_MAP.get(x)
)

script_type = st.segmented_control(
    "Script type",
    ["simplified", "traditional"],
    selection_mode="single",
    format_func=lambda x: {"simplified": "Simplified", "traditional": "Traditional"}.get(x),
    default="traditional"
)

if st.button("Simplify"):
    to_simplify = None
    if len(input_text):
        to_simplify = input_text
    elif 'wiki_summary' in st.session_state:
        to_simplify = st.session_state.wiki_summary
    else:
        st.warning("No text to simplify.")
    
    if to_simplify is not None:
        st.write("Original:")
        st.write(to_simplify)

        st.write("Simplified Text:")
        if contains_chinese(to_simplify):
            instruction = open(f"./{script_type}.prompt", "r").read()
            with st.spinner("Simplifying text..."):
                result = simplify_text(instruction, to_simplify, level, script_type)
                st.write_stream(result)
            st.caption("Note: responses generated via LLM (GLM-4). LLMs may hallucinate, and responses are not guaranteed to be well-calibrated to the level specified.")
        else:
            st.warning(f"String does not contain valid Chinese characters: {to_simplify}")
    
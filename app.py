import streamlit as st
from ask import hybrid_search, generate_answer


st.set_page_config(
    page_title="UTI Clinical Decision Support",
    page_icon="🩺",
    layout="wide"
)


st.title("🩺 UTI Clinical Decision Support")
st.caption("Hybrid Retrieval + Evidence-Based Recommendations")

st.divider()


question = st.text_area(
    "Enter your clinical question:",
    placeholder="Example: What antibiotics are recommended for non-pregnant women aged 16 years and over?",
    height=120
)


if st.button("Get Recommendation", type="primary"):

    if not question.strip():
        st.warning("Please enter a clinical question.")

    else:

        with st.spinner("Searching clinical evidence..."):

            results = hybrid_search(
                question.strip(),
                top_k=5
            )

        if not results:

            st.error("No evidence found.")

        else:

            best = results[0]
            metadata = best["metadata"]

            answer = generate_answer(
                question.strip(),
                best
            )

            st.subheader("Answer")

            st.markdown(answer)

            st.divider()

            st.subheader("Source")

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    "**Source ID:**",
                    metadata.get("source_id")
                )

                st.write(
                    "**Source Type:**",
                    metadata.get("source_type")
                )

            with col2:
                st.write(
                    "**Title:**",
                    metadata.get("title")
                )

                st.write(
                    "**Page(s):**",
                    metadata.get("pages")
                )

            st.metric(
                "Hybrid Score",
                round(best["hybrid_score"], 4)
            )

            st.divider()

            st.subheader("Evidence")

            st.info(best["document"])

            st.divider()

            st.subheader("Other Retrieved Sources")

            for i, result in enumerate(results[1:], start=2):

                meta = result["metadata"]

                st.write(
                    f"{i}. "
                    f"{meta.get('source_id')} | "
                    f"{meta.get('source_type')} | "
                    f"Score: {result['hybrid_score']:.4f}"
                )
.PHONY: test streamlit

test:
	pytest -q

streamlit:
	streamlit run src/streamlit_app.py

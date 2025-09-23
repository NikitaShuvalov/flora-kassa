run:
	python3 -m uvicorn main:app --reload

desktop:
	cd desktop && npm start http://127.0.0.1:8000

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /learner
COPY --chown=65534:65534 client.py /learner/client.py
USER 65534:65534
CMD ["python", "-B", "/learner/client.py"]

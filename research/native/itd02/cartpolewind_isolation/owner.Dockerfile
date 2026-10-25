FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /sealed
COPY --chown=65534:65534 owner.py /sealed/owner.py
COPY --chown=65534:65534 source_original.py /sealed/source_original.py
COPY --chown=65534:65534 private_canary.txt /sealed/private_canary.txt
USER 65534:65534
EXPOSE 8765
CMD ["python", "-B", "/sealed/owner.py"]

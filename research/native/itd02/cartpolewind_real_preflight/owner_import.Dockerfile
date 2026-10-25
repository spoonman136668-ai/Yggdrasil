FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN python -m pip install --disable-pip-version-check --no-cache-dir numpy==1.26.4 gymnasium==0.29.1 networkx==3.2.1 toposort==1.10 pydash==7.0.7
WORKDIR /sealed
COPY --chown=65534:65534 owner_authentic.py /sealed/owner.py
COPY --chown=65534:65534 source_original.py /sealed/source_original.py
COPY --chown=65534:65534 private_canary.txt /sealed/private_canary.txt
COPY --chown=65534:65534 causal_gym/ /sealed/upstream/causal_gym/
USER 65534:65534
EXPOSE 8765
CMD ["python", "-B", "/sealed/owner.py"]

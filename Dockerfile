FROM condaforge/mambaforge:latest

COPY . /app

# Create volumes for persistent data
VOLUME [ "/app/logs", "/app/output" ]

# Install make
RUN apt update && apt install make -y

# Create new conda environment
RUN conda create -n nss python=3.11

# Set workdir
WORKDIR /app

# Install dependencies
SHELL ["conda", "run", "-n", "nss", "/bin/bash", "-c"]
RUN pip install -r requirements.txt

ENTRYPOINT ["/bin/bash"]
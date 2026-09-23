# Includes Linux, Python, CUDA runtime, and CUDA-enabled PyTorch.
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY container_nautilus_gpu_test.py .

# Default behavior: Task 1 GPU verification program runs automatically.
# For Task 2, the Kubernetes Job will override this default command
# while using this exact same image.
ENTRYPOINT ["python"]
CMD ["container_nautilus_gpu_test.py"]
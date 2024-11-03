# Use a slim version of Python 3.12 as the base image
FROM python:3.12.0-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the installed packages from the builder stage
FROM python:3.12.0-slim
WORKDIR /app
COPY --from=builder /app /app
COPY . .

# Expose port 8080 for the application
EXPOSE 8080

# Set environment variables for the API keys
ENV GROQ_API_KEY='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'
ENV HUGGINGFACEHUB_API_TOKEN='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'

# Specify the command to run the application
ENTRYPOINT ["uvicorn", "src.main:app"]

# Set default command-line arguments for the ENTRYPOINT
CMD ["--port", "8080", "--host", "0.0.0.0"]

# Stage 1: builder (build wheels)
FROM python:3.11-slim AS builder
WORKDIR /wheels
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential python3-dev && \
    pip install --upgrade pip wheel && \
    pip wheel --no-deps --wheel-dir /wheels -r requirements.txt && \
    apt-get remove -y build-essential python3-dev && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Stage 2: runtime
FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# install cron and tzdata for timezone management
RUN apt-get update && apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# copy wheels and install dependencies
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl

# copy application code and keys
COPY app /app
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# set permissions and install cron file
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# create persistent volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Start cron and the API server. Use bash to run both.
CMD ["bash", "-lc", "service cron start && uvicorn main:app --host 0.0.0.0 --port 8080"]

FROM frappe/erpnext:latest

# Copy LaundryCloud app
COPY laundrycloud /home/frappe/frappe-bench/apps/laundrycloud

# Install dependencies
RUN cd /home/frappe/frappe-bench/apps/laundrycloud && \
    pip install -r requirements.txt

# Add app to apps.txt
RUN echo "laundrycloud" >> /home/frappe/frappe-bench/apps.txt

# Build assets
RUN cd /home/frappe/frappe-bench && \
    bench build --app laundrycloud

EXPOSE 8000
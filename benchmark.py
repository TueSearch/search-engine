import random
import string
import time
import mysql.connector

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'tuesearch',
    'raise_on_warnings': True
}

# Function to generate random URL
def generate_random_url():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f'https://{random_string}.com'

# Function to generate random string
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Generate random data
num_records = 10000
data = []
for _ in range(num_records):
    url = generate_random_url()
    server = ''.join(random.choices(string.ascii_lowercase, k=10))
    title = generate_random_string(50)
    body = generate_random_string(200)
    title_tokens = generate_random_string(100)
    body_tokens = generate_random_string(500)
    all_harvested_links = generate_random_string(100)
    relevant_links = generate_random_string(100)
    relevant = random.choice([0, 1])
    data.append((url, server, title, body, title_tokens, body_tokens, all_harvested_links, relevant_links, relevant))

# Benchmark insertion speed of insert_document and insert_job
try:
    # Connect to MySQL
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Benchmark insert_document
    start_time = time.time()
    for record in data:
        cursor.execute('SELECT insert_document(%s, %s, %s, %s, %s, %s, %s, %s, %s)', record)
        connection.commit()
    end_time = time.time()
    print(f'insert_document - Time taken: {end_time - start_time:.4f} seconds')

    # Benchmark insert_job
    start_time = time.time()
    for record in data:
        cursor.execute('SELECT insert_job(%s, %s, %s)', record[:3])
        connection.commit()
    end_time = time.time()
    print(f'insert_job - Time taken: {end_time - start_time:.4f} seconds')

except mysql.connector.Error as error:
    print(f'MySQL Error: {error}')

finally:
    # Close the connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print('MySQL connection closed')

import http.client
import json

PORT = 8000
SERVER = "127.0.0.1"

# Client for testing the advanced level, related to the json part.
# I have tested here each resource of the server but with the purpose of obtaining the information in json format.

print("\nConnecting to server: {}:{}\n".format(SERVER, PORT))

# List with the urls I want to test

my_url = ["/listSpecies?json=1", "/listSpecies?limit=10&json=1", "/karyotype?specie=sheep&json=1",
          "/chromosomeLength?specie=human&chromo=3&json=1", "/geneSeq?gene=FRAT2&json=1",
          "/geneInfo?gene=FRAT2&json=1", "/geneCalc?gene=FRAT2&json=1",
          "/geneList?chromo=4&start=1&end=3000000&json=1"]

number = 1

conn = http.client.HTTPConnection(SERVER, PORT)

# Loop for requesting each url to the server

for url in my_url:
    print("--------------------------------------")
    print("TEST ", number)
    conn.request("GET", url)
    r1 = conn.getresponse()
    print("Response received!: {} {}\n".format(r1.status, r1.reason))
    data1 = r1.read().decode("utf-8")
    response = json.loads(data1)
    print(response)
    number += 1
